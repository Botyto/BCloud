from datetime import datetime, timezone
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session
from uuid import UUID

from . import fspath
from .contents import FileContents, NAMESPACE_CONTENT
from .errors import *
from .storage import StorageManager
from ..data import FileMetadata, FileStorage, FileType
from ..data import DIRECTORY_MIME, LINK_MIME

from core.api.pages import PagesInput
from core.auth.handlers import AuthError
from core.data.blobs.base import Blobs
from core.data.sql.columns import ensure_str_fit



class FileManager:
    SERVICE_PREFIX = "__app_"

    blobs: Blobs
    user_id: UUID
    session: Session
    _contents: FileContents|None = None
    _storage: StorageManager|None = None

    @property
    def contents(self):
        if self._contents is None:
            self._contents = FileContents(self.blobs, NAMESPACE_CONTENT)
        return self._contents
    
    @property
    def storage(self):
        if self._storage is None:
            self._storage = StorageManager(self.user_id, self.session)
        return self._storage

    def __init__(self, blobs: Blobs, user_id: UUID, session: Session):
        self.blobs = blobs
        self.user_id = user_id
        self.session = session

    def _follow_link(self, metadata: FileMetadata|None) -> FileMetadata|None:
        if metadata is not None and metadata.type == FileType.LINK:
            linked_id = self.contents.read(metadata).decode("utf-8")
            linked_file = self.by_id(UUID(linked_id))
            return linked_file

    def by_path(self, path: str, *, follow_last_link: bool = True):
        storage_id, parts = fspath.get_parts(path)
        if storage_id is None:
            return None
        statement = select(FileStorage) \
            .where(FileStorage.id == storage_id) \
            .where(FileStorage.user_id == self.user_id)
        storage = self.session.scalars(statement).one()
        dir = storage.root_dir
        for step in parts:
            dir = self._follow_link(dir)
            if dir is None:
                break
            dir = dir.get_child(step)
            if dir is None or not dir.isdir:
                break
        if dir is not None and follow_last_link:
            dir = self._follow_link(dir)
        return dir
    
    def by_id(self, id: UUID):
        statement = select(FileMetadata) \
            .where(FileMetadata.id == id)
        file = self.session.scalars(statement).one()
        if file.user_id != self.user_id:
            raise AuthError()
        return file
    
    def exists(self, path: str):
        return self.by_path(path) is not None
    
    def makefile(self, path: str, mime_type: str|None = None):
        if mime_type is not None:
            ensure_str_fit("MIME-Type", mime_type, FileMetadata.mime_type)
        basename = fspath.basename(path)
        ensure_str_fit("File name", basename, FileMetadata.name)
        dir_path = fspath.dirname(path)
        dir = self.by_path(dir_path)
        if dir is None:
            raise DirectoryNotFound(path)
        old_file = dir.get_child(basename)
        if old_file is not None:
            raise FileAlreadyExists(path)
        now = datetime.now().astimezone(timezone.utc)
        file = FileMetadata(
            name=basename,
            mime_type=mime_type,
            size=0,
            parent=dir,
            storage=dir.storage,
            atime=now,
            mtime=now,
            ctime=now)
        self.session.add(file)
        return file
    
    def copyfile(self, src: str, dst: str):
        src_storage, _ = fspath.strip_storage(src)
        dst_storage, _ = fspath.strip_storage(dst)
        if src_storage != dst_storage:
            raise ValueError("Cannot copy files between storages")
        src_file = self.by_path(src)
        if src_file is None:
            raise FileNotFoundError(src)
        dst_file = self.makefile(dst, src_file.mime_type)
        self.contents.copy(src_file, dst_file)
        dst_file.ctime_utc = src_file.ctime_utc
        dst_file.mtime_utc = src_file.mtime_utc
        dst_file.atime_utc = src_file.atime_utc
        return dst_file
    
    def makedirs(self, path: str):
        storage_id, parts = fspath.get_parts(path)
        if storage_id is None:
            raise StorageNotSpecified(path)
        storage = self.storage.get(storage_id)
        dir = storage.root_dir
        for i, parti in enumerate(parts):
            nextdir = dir.get_child(parti)
            nextdir = self._follow_link(nextdir)
            if nextdir is None or not nextdir.isdir:
                now = datetime.now().astimezone(timezone.utc)
                for j, partj in enumerate(parts):
                    ensure_str_fit("Directory name", partj, FileMetadata.name)
                for j in range(i, len(parts)):
                    partj = parts[j]
                    newdir = FileMetadata(
                        name=partj,
                        mime_type=DIRECTORY_MIME,
                        size=0,
                        parent=dir,
                        storage=dir.storage,
                        atime=now,
                        mtime=now,
                        ctime=now)
                    self.session.add(newdir)
                    dir = newdir
                break
            else:
                dir = nextdir
        return dir
    
    def makelink(self, path: str, target: str):
        target_meta = self.by_path(target)
        if target_meta is None:
            raise FileNotFoundError(target)
        link = self.makefile(path, LINK_MIME)
        link_content = str(target_meta.id).encode("utf-8")
        self.contents.write(link, link_content)
        return link
    
    def delete(self, path: str):
        metadata = self.by_path(path)
        if metadata is None:
            raise FileNotFoundError(path)
        if metadata.isfile:
            self.contents.delete(metadata)
        elif metadata.isdir:
            raise NotImplementedError()
        self.session.delete(metadata)
        # TODO delete links to this file

    def rename(self, src: str, dst: str):
        src_storage, _ = fspath.strip_storage(src)
        dst_storage, _ = fspath.strip_storage(dst)
        if src_storage != dst_storage:
            raise Exception("Cannot rename across storages")
        src_meta = self.by_path(src)
        if src_meta is None:
            raise FileNotFoundError(src)
        dst_dir = fspath.dirname(dst)
        dst_dir_meta = self.by_path(dst_dir)
        if dst_dir_meta is None or not dst_dir_meta.isdir:
            raise DirectoryNotFound(dst)
        dst_basename = fspath.basename(dst)
        dst_meta = dst_dir_meta.get_child(dst_basename)
        if dst_meta is not None:
            raise FileAlreadyExists(dst)
        src_meta.parent = dst_dir_meta
        src_meta.name = dst_basename
        src_meta.modified()
        return src_meta
