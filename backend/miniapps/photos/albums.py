from typing import List
from uuid import UUID

from sqlalchemy import select

from core.api.modules.gql import GqlMiniappModule, query, mutation
from core.api.pages import PagesInput, PagesResult

from .data import PhotoAlbumKind, PhotoAlbum, PhotoAlbumEntry
from .tools.album import PhotoAlbumManager


class AlbumsModule(GqlMiniappModule):
    _albums: PhotoAlbumManager|None = None

    @property
    def albums(self):
        if self._albums is None:
            self._albums = PhotoAlbumManager(self.user_id, self.context, self.session)
        return self._albums

    @query()
    def list(self, kind: PhotoAlbumKind, pages: PagesInput) -> PagesResult[PhotoAlbum]:
        statement = select(PhotoAlbum) \
            .filter(PhotoAlbum.user_id == self.user_id) \
            .filter(PhotoAlbum.kind == kind) \
            .order_by(PhotoAlbum.created_at_utc.desc())
        return pages.of(self.session, statement)
    
    @query()
    def by_id(self, id: UUID) -> PhotoAlbum:
        statement = select(PhotoAlbum) \
            .filter(PhotoAlbum.user_id == self.user_id) \
            .filter(PhotoAlbum.id == id)
        return self.session.scalars(statement).one()

    @query()
    def by_slug(self, slug: str) -> PhotoAlbum:
        statement = select(PhotoAlbum) \
            .filter(PhotoAlbum.user_id == self.user_id) \
            .filter(PhotoAlbum.slug == slug)
        return self.session.scalars(statement).one()
    
    @mutation()
    def create(self, name: str, kind: PhotoAlbumKind, asset_ids: List[UUID]|None = None) -> PhotoAlbum:
        return self.albums.create(name, kind, asset_ids)
    
    @mutation()
    def add_asset(self, album_id: UUID, asset_id: UUID) -> PhotoAlbumEntry:
        return self.albums.add_asset(album_id, asset_id)
    
    @mutation()
    def add_text(self, album_id: UUID, text: str) -> PhotoAlbumEntry:
        return self.albums.add_text(album_id, text)
    
    @mutation()
    def add_location(self, album_id: UUID, latitude: float, longitude: float) -> PhotoAlbumEntry:
        return self.albums.add_location(album_id, latitude, longitude)
    
    @mutation()
    def add_map(self, album_id: UUID, src_latitude: float, src_longitude: float, dst_latitude: float, dst_longitude: float) -> PhotoAlbumEntry:
        return self.albums.add_map(album_id, src_latitude, src_longitude, dst_latitude, dst_longitude)
