from typing import List
from uuid import UUID

from core.asyncjob.context import AsyncJobContext
from core.auth.access import AccessLevel
from core.data.sql.database import Session

from ..data import PhotoAlbum, PhotoAlbumKind, PhotoAlbumEntry, PhotoAlbumEntryKind
from ..data import PhotoAsset


class PhotoAlbumManager:
    user_id: UUID|None
    context: AsyncJobContext
    service: bool
    _session: Session|None = None

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

    def create(self, name: str, kind: PhotoAlbumKind, asset_ids: List[UUID]|None = None):
        album = PhotoAlbum(
            user_id=self.user_id,
            name=name,
            kind=kind,
        )
        if kind == PhotoAlbumKind.SHARED:
            album.access = AccessLevel.PUBLIC_READABLE
        self.session.add(album)
        self.session.commit()
        if asset_ids:
            for asset_id in asset_ids:
                self.add_asset(album.id, asset_id, autocommit=False)
            self.session.commit()
        return album

    def add_asset(self, album_id: UUID, asset_id: UUID, autocommit: bool = True):
        album = self.session.get(PhotoAlbum, album_id)
        if album is None:
            raise ValueError(f"Album {album_id} not found")
        asset = self.session.get(PhotoAsset, asset_id)
        if asset is None:
            raise ValueError(f"Asset {asset_id} not found")
        entry = PhotoAlbumEntry(
            sort_key = len(album.entries),
            album = album,
            kind = PhotoAlbumEntryKind.ASSET,
            asset = asset,
        )
        album.entries.append(entry)
        if autocommit:
            self.session.commit()
        return entry
    
    def add_text(self, album_id: UUID, text: str, autocommit: bool = True):
        album = self.session.get(PhotoAlbum, album_id)
        if album is None:
            raise ValueError(f"Album {album_id} not found")
        entry = PhotoAlbumEntry(
            sort_key = len(album.entries),
            album = album,
            kind = PhotoAlbumEntryKind.TEXT,
            text = text,
        )
        album.entries.append(entry)
        if autocommit:
            self.session.commit()
        return entry
    
    def add_location(self, album_id: UUID, latitude: float, longitude: float, autocommit: bool = True):
        album = self.session.get(PhotoAlbum, album_id)
        if album is None:
            raise ValueError(f"Album {album_id} not found")
        entry = PhotoAlbumEntry(
            sort_key = len(album.entries),
            album = album,
            kind = PhotoAlbumEntryKind.LOCATION,
            src_latitude = latitude,
            src_longitude = longitude,
        )
        album.entries.append(entry)
        if autocommit:
            self.session.commit()
        return entry
    
    def add_map(self,
        album_id: UUID,
        src_latitude: float, src_longitude: float,
        dst_latitude: float, dst_longitude: float,
        autocommit: bool = True
    ):
        album = self.session.get(PhotoAlbum, album_id)
        if album is None:
            raise ValueError(f"Album {album_id} not found")
        entry = PhotoAlbumEntry(
            sort_key = len(album.entries),
            album = album,
            kind = PhotoAlbumEntryKind.MAP,
            src_latitude = src_latitude,
            src_longitude = src_longitude,
            dst_latitude = dst_latitude,
            dst_longitude = dst_longitude,
        )
        album.entries.append(entry)
        if autocommit:
            self.session.commit()
        return entry
