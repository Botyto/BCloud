from dataclasses import dataclass
from datetime import date
from typing import List
from uuid import UUID

import sqlalchemy
from sqlalchemy import select

from core.api.pages import PagesInput, PagesResult
from core.api.modules.gql import GqlMiniappModule, query, mutation

from .data import PhotoAsset, PhotoAssetKind
from .tools.asset import PhotoAssetManager


@dataclass
class TimelineLayout:
    date: date
    count: int


class AssetsModule(GqlMiniappModule):
    _assets: PhotoAssetManager

    @property
    def assets(self) -> PhotoAssetManager:
        if self._assets is None:
            self._assets = PhotoAssetManager(self.user_id, self.context, self.session)
        return self._assets

    @query()
    def timeline_layout(self) -> List[TimelineLayout]:
        statement = select(PhotoAsset) \
            .where(PhotoAsset.user_id == self.user_id) \
            .group_by(PhotoAsset.created_at_utc) \
            .order_by(PhotoAsset.created_at_utc.desc()) \
            .add_columns(sqlalchemy.func.count(PhotoAsset.id))
        rows = self.session.scalars(statement).all()
        return [TimelineLayout(row.PhotoAsset.added_at_utc.date(), row.count) for row in rows]
    
    @query()
    def by_date_range(self, date_from: date, date_to: date) -> List[PhotoAsset]:
        statement = select(PhotoAsset) \
            .where(PhotoAsset.user_id == self.user_id) \
            .where(PhotoAsset.created_at_utc >= date_from) \
            .where(PhotoAsset.created_at_utc <= date_to)
        return list(self.session.scalars(statement).all())

    @query()
    def by_tag(self, tag: str, pages: PagesInput) -> PagesResult[PhotoAsset]:
        statement = select(PhotoAsset) \
            .where(PhotoAsset.user_id == self.user_id) \
            .where(PhotoAsset.tags.any(tag=tag))
        return pages.of(self.session, statement)
    
    @query()
    def get(self, id: UUID) -> PhotoAsset:
        statement = select(PhotoAsset).where(PhotoAsset.id == id)
        return self.session.scalars(statement).one()
    
    @mutation()
    def create(self, kind: PhotoAssetKind) -> PhotoAsset:
        return self.assets.create(kind)
