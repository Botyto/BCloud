from sqlalchemy import select
from sqlalchemy.orm import InstrumentedAttribute
from uuid import UUID

from core.asyncjob.context import AsyncJobContext
from core.data.sql.database import Session

from miniapps.files.data import FileStorage, FileMetadata
from miniapps.files.tools import fspath
from miniapps.files.tools.files import FileManager
from miniapps.files.tools.storage import StorageManager

from ..data import PhotoAsset

from .importing import PhotoImporter


class PhotoFileManager:
    STORAGE_NAME = StorageManager.SERVICE_PREFIX + "photos"

    user_id: UUID|None
    context: AsyncJobContext
    service: bool
    _session: Session|None = None
    _files: FileManager|None = None

    @property
    def files(self):
        if self._files is None:
            if self.user_id is not None:
                self._files = FileManager(self.context.blobs, self.user_id, self.session, service=self.service)
            else:
                self._files = FileManager.for_service(self.context.blobs, self.session)
        return self._files
    
    @property
    def contents(self):
        return self.files.contents
    
    @property
    def session(self):
        if self._session is None:
            self._session = self.context.database.make_session()
        return self._session

    def __init__(self, user_id: UUID|None, context: AsyncJobContext, session: Session, service: bool = False):
        self.user_id = user_id
        self.context = context
        self._session = session
        self.service = service

    @classmethod
    def for_service(cls, user_id: UUID|None, context: AsyncJobContext, session: Session):
        return cls(user_id, context, session, service=True)
    
    def _file_path(self, storage: FileStorage, asset: PhotoAsset):
        return fspath.join(storage.id, str(asset.id))

    def _get_asset(self, asset: UUID|PhotoAsset) -> PhotoAsset|None:
        if isinstance(asset, UUID):
            statement = select(PhotoAsset) \
                .filter(PhotoAsset.id == asset)
            if self.user_id is not None:
                statement = statement.filter(PhotoAsset.user_id == self.user_id)
            return self.session.scalars(statement).one_or_none()
        return asset

    def write(self, asset: PhotoAsset, content: bytes, mime_type: str):
        return self.write_any(asset, PhotoAsset.file, content, mime_type)

    def write_any(self, asset: PhotoAsset, attr: InstrumentedAttribute[FileMetadata|None], content: bytes, mime_type: str):
        file: FileMetadata
        if asset.file is None:
            storage = self.files.storage.get_or_create(self.STORAGE_NAME)
            if self.session.is_modified(storage):
                self.session.commit()
            path = self._file_path(storage, asset)
            file = self.files.makefile(path, mime_type, make_dirs=True)
            setattr(asset, attr.key, file)
            self.session.add(file)
        else:
            file = getattr(asset, attr.key)
        self.contents.write(file, content, mime_type)
        if attr is PhotoAsset.file:
            importing = PhotoImporter(self.context, self.session)
            importing.update_exif_info(asset)
            importing.update_previews(asset)

    def read(self, asset: PhotoAsset):
        return self.read_any(asset, PhotoAsset.file)

    def read_any(self, asset: PhotoAsset, attr: InstrumentedAttribute[FileMetadata|None]):
        file: FileMetadata|None = getattr(asset, attr.key)
        if file is None:
            return b''
        return self.contents.read(file)
