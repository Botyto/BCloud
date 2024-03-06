from datetime import datetime, timezone
import mimetypes
from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID

from . import fspath
from .contents import FileContents, NAMESPACE_CONTENT
from .errors import *
from .storage import StorageManager
from ..data import FileMetadata, FileType
from ..data import DIRECTORY_MIME, LINK_MIME

from core.data.blobs.base import Blobs
from core.data.sql.columns import ensure_str_fit


class FileManager:
    SERVICE_PREFIX = "__app_"

    blobs: Blobs
    user_id: UUID|None
    session: Session
    service: bool = False
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
            self._storage = StorageManager(self.user_id, self.session, service=self.service)
        return self._storage

    def __init__(self, blobs: Blobs, user_id: UUID|None, session: Session, service: bool = False):
        self.blobs = blobs
        self.user_id = user_id
        self.session = session
        self.service = service

    @classmethod
    def for_service(cls, blobs: Blobs, session: Session):
        return cls(blobs, None, session, service=True)

    def _follow_link(self, metadata: FileMetadata|None) -> FileMetadata|None:
        if metadata is not None and metadata.type == FileType.LINK:
            linked_id = self.contents.read(metadata).decode("utf-8")
            linked_file = self.by_id(UUID(linked_id))
            return linked_file
        return metadata

    def by_path(self, path: str, *, follow_last_link: bool = True):
        storage_id, parts = fspath.get_parts(path)
        if storage_id is None:
            return None
        dir = self.storage.root(storage_id)
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
        return file
    
    def exists(self, path: str):
        return self.by_path(path) is not None
    
    def unique_name(self, path: str):
        if not self.exists(path):
            return path
        ext = fspath.ext(path)
        base_path = path[:-len(ext)]
        i = 2
        while True:
            new_path = f"{base_path} ({i}){ext}"
            if not self.exists(new_path):
                return new_path
            i += 1
    
    def makefile(self, path: str, mime_type: str|None = None, make_dirs: bool = False):
        if not mime_type:
            mime_type = mimetypes.guess_type(path)[0]
        if mime_type is not None:
            ensure_str_fit("MIME-Type", mime_type, FileMetadata.mime_type)
        basename = fspath.basename(path)
        if not basename:
            raise ValueError("File name cannot be empty")
        ensure_str_fit("File name", basename, FileMetadata.name)
        dir_path = fspath.normpath(fspath.dirname(path))
        if make_dirs:
            dir = self.makedirs(dir_path)
        else:
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
            parent=dir,
            storage=dir.storage,
            atime_utc=now,
            mtime_utc=now,
            ctime_utc=now)
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
        if src_file.isroot:
            raise ValueError("Cannot copy root directory")
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
        dir = self.storage.root(storage_id)
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
                        parent=dir,
                        storage=dir.storage,
                        atime_utc=now,
                        mtime_utc=now,
                        ctime_utc=now)
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
        if metadata.isroot:
            raise ValueError("Cannot delete root directory")
        if metadata.isfile or metadata.isdir:
            self.contents.delete(metadata)
        self.session.delete(metadata)
        # TODO delete links to this file

    def rename(self, src: str, dst: str):
        src_storage, src_path = fspath.strip_storage(src)
        dst_storage, dst_path = fspath.strip_storage(dst)
        if src_storage != dst_storage:
            raise Exception("Cannot rename across storages")
        src_meta = self.by_path(src)
        if src_meta is None:
            raise FileNotFoundError(src)
        if src_meta.isroot:
            raise ValueError("Cannot rename root directory")
        if not isinstance(src_storage, UUID):
            src = fspath.join(src_meta.storage_id, src_path)
        if not isinstance(dst_storage, UUID):
            dst = fspath.join(src_meta.storage_id, dst_path)
        dst_dir = fspath.normpath(fspath.dirname(dst))
        dst_dir_meta = self.by_path(dst_dir)
        if dst_dir_meta is None or not dst_dir_meta.isdir:
            raise DirectoryNotFound(dst)
        dst_basename = fspath.basename(dst)
        if not dst_basename:
            raise ValueError("File name cannot be empty")
        ensure_str_fit("File name", dst_basename, FileMetadata.name)
        dst_meta = dst_dir_meta.get_child(dst_basename)
        if dst_meta is not None:
            raise FileAlreadyExists(dst)
        self.contents.rename(src_meta, dst)
        src_meta.parent = dst_dir_meta
        src_meta.name = dst_basename
        src_meta.modified()
        return src_meta
