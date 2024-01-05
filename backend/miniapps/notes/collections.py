from enum import Enum
from uuid import UUID

from sqlalchemy import delete, select, update, Select

from core.api.modules.gql import GqlMiniappModule, query, mutation
from core.api.pages import PagesInput, PagesResult
from core.data.sql.columns import ensure_str_fit
from core.graphql.result import SuccessResult

from .data import NotesCollection, CollectionView


class ArchivedFilter(Enum):
    ALL = "all"
    ARCHIVED = "archived"
    NOT_ARCHIVED = "not_archived"

    def filter(self, statement: Select):
        if self == ArchivedFilter.ARCHIVED:
            return statement.where(NotesCollection.archived == True)
        elif self == ArchivedFilter.NOT_ARCHIVED:
            return statement.where(NotesCollection.archived == False)
        return statement


class CollectionsModule(GqlMiniappModule):
    def _list(self, parent_id_or_slug: UUID|str|None, archived: ArchivedFilter, pages: PagesInput) -> PagesResult[NotesCollection]:
        statement = select(NotesCollection)
        if isinstance(parent_id_or_slug, str):
            statement = statement.where(NotesCollection.parent.has(slug=parent_id_or_slug))
        else:
            statement = statement.where(NotesCollection.parent_id == parent_id_or_slug)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        statement = archived.filter(statement)
        return pages.of(self.session, statement)
    
    @query()
    def list_by_id(self, parent_id: UUID|None, archived: ArchivedFilter, pages: PagesInput) -> PagesResult[NotesCollection]:
        return self._list(parent_id, archived, pages)
    
    @query()
    def list_by_slug(self, parent_slug: str|None, archived: ArchivedFilter, pages: PagesInput) -> PagesResult[NotesCollection]:
        return self._list(parent_slug, archived, pages)

    def _create(self, name: str, parent_id_or_slug: UUID|str|None, view: CollectionView = CollectionView.NOTES) -> NotesCollection:
        ensure_str_fit("name", name, NotesCollection.name)
        if isinstance(parent_id_or_slug, str):
            statement = select(NotesCollection.id) \
                .where(NotesCollection.slug == parent_id_or_slug)
            parent_id = self.session.scalars(statement).one()
        else:
            parent_id = parent_id_or_slug
        collection = NotesCollection(
            user_id=self.user_id,
            parent_id=parent_id,
            name=name,
            view=view,
        )
        self.session.add(collection)
        self.session.commit()
        self.log_activity("collection.create", {"id": str(collection.id), "name": name, "view": view.value})
        return collection
    
    @mutation()
    def create_with_id(self, name: str, parent_id: UUID|None, view: CollectionView = CollectionView.NOTES) -> NotesCollection:
        return self._create(name, parent_id, view)

    @mutation()
    def create_with_slug(self, name: str, parent_slug: str|None, view: CollectionView = CollectionView.NOTES) -> NotesCollection:
        return self._create(name, parent_slug, view)
    
    def _get(self, id_or_slug: UUID|str) -> NotesCollection:
        statement = select(NotesCollection)
        if isinstance(id_or_slug, str):
            statement = statement.where(NotesCollection.slug == id_or_slug)
        else:
            statement = statement.where(NotesCollection.id == id_or_slug)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        return self.session.scalars(statement).one()
    
    @query()
    def get_by_id(self, id: UUID) -> NotesCollection:
        return self._get(id)

    @query()
    def get_by_slug(self, slug: str) -> NotesCollection:
        return self._get(slug)

    def _delete(self, id_or_slug: UUID|str) -> SuccessResult:
        statement = delete(NotesCollection) \
            .returning(NotesCollection.name, NotesCollection.id)
        if isinstance(id_or_slug, str):
            statement = statement.where(NotesCollection.slug == id_or_slug)
        else:
            statement = statement.where(NotesCollection.id == id_or_slug)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        result = self.session.execute(statement)
        name, id = result.scalar_one()
        self.log_activity("collection.delete", {"id": str(id), "name": name})
        return SuccessResult()
    
    @mutation()
    def delete_by_id(self, id: UUID) -> SuccessResult:
        return self._delete(id)
    
    @mutation()
    def delete_by_slugs(self, slug: str) -> SuccessResult:
        return self._delete(slug)

    def _rename(self, id_or_slug: UUID|str, name: str) -> NotesCollection:
        ensure_str_fit("name", name, NotesCollection.name)
        statement = select(NotesCollection)
        if isinstance(id_or_slug, str):
            statement = statement.where(NotesCollection.slug == id_or_slug)
        else:
            statement = statement.where(NotesCollection.id == id_or_slug)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        collection = self.session.scalars(statement).one()
        old_name = collection.name
        collection.name = name
        self.session.commit()
        self.log_activity("collection.rename", {"id": str(collection.id), "new": name, "old": old_name})
        return collection
    
    @mutation()
    def rename_by_id(self, id: UUID, name: str) -> NotesCollection:
        return self._rename(id, name)

    @mutation()
    def rename_by_slug(self, slug: str, name: str) -> NotesCollection:
        return self._rename(slug, name)
    
    def _set_archived(self, id_or_slug: UUID|str, archived: bool) -> NotesCollection:
        statement = update(NotesCollection) \
            .values(archived=archived) \
            .returning(NotesCollection)
        if isinstance(id_or_slug, str):
            statement = statement.where(NotesCollection.slug == id_or_slug)
        else:
            statement = statement.where(NotesCollection.id == id_or_slug)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        collection = self.session.scalars(statement).one()
        self.log_activity("collection.set_archived", {"id": str(collection.id), "archived": archived})
        return collection
    
    @mutation()
    def archive_by_id(self, id: UUID) -> NotesCollection:
        return self._set_archived(id, True)
    
    @mutation()
    def archive_by_slug(self, slug: str) -> NotesCollection:
        return self._set_archived(slug, True)

    def _reparent(self, id_or_slug: UUID|str, parent_id_or_slug: UUID|str|None) -> NotesCollection:
        statement = select(NotesCollection)
        if isinstance(id_or_slug, str):
            statement = statement.where(NotesCollection.slug == id_or_slug)
        else:
            statement = statement.where(NotesCollection.id == id_or_slug)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        collection = self.session.scalars(statement).one()
        if isinstance(parent_id_or_slug, str):
            statement = select(NotesCollection.id) \
                .where(NotesCollection.slug == parent_id_or_slug)
            parent_id = self.session.scalars(statement).one()
        else:
            parent_id = parent_id_or_slug
        old_parent_id = collection.parent_id
        collection.parent_id = parent_id
        self.session.commit()
        self.log_activity("collection.reparent", {"id": str(collection.id), "new": parent_id, "old": old_parent_id})
        return collection
    
    @mutation()
    def reparent_by_id(self, id: UUID, parent_id: UUID|None) -> NotesCollection:
        return self._reparent(id, parent_id)
    
    @mutation()
    def reparent_by_slug(self, slug: str, parent_slug: str|None) -> NotesCollection:
        return self._reparent(slug, parent_slug)
