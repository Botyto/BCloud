from uuid import UUID

from sqlalchemy import select

from core.asyncjob.context import AsyncJobContext
from core.data.sql.database import Session

from ..data import PhotoAsset, PhotoAssetKind

from .files import PhotoFileManager
from .importing import PREVIEW_MIME


class PhotoAssetManager:
    user_id: UUID|None
    context: AsyncJobContext
    service: bool
    _session: Session|None = None
    _files: PhotoFileManager|None = None

    @property
    def session(self):
        if self._session is None:
            self._session = self.context.database.make_session()
        return self._session
    
    @property
    def files(self):
        if self._files is None:
            self._files = PhotoFileManager(self.user_id, self.context, self.session, self.service)
        return self._files

    def __init__(self, user_id: UUID|None, context: AsyncJobContext, session: Session, service: bool = False):
        self.user_id = user_id
        self.context = context
        self._session = session
        self.service = service

    @classmethod
    def for_service(cls, user_id: UUID|None, context: AsyncJobContext, session: Session):
        return cls(user_id, context, session, service=True)
    
    def get(self, asset_id: UUID):
        statement = select(PhotoAsset).where(PhotoAsset.id == asset_id)
        return self.session.scalars(statement).one()

    def create(self, kind: PhotoAssetKind):
        if self.user_id is None:
            raise ValueError("Cannot create asset without user_id")
        asset = PhotoAsset()
        asset.user_id = self.user_id
        asset.kind = kind
        self.files.get_any(asset, PhotoAsset.file, create=True, mime_type=None)
        self.files.get_any(asset, PhotoAsset.preview, create=True, mime_type=PREVIEW_MIME)
        self.files.get_any(asset, PhotoAsset.thumbnail, create=True, mime_type=PREVIEW_MIME)
        self.session.add(asset)
        return asset
