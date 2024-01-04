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
    @query()
    def list(self, parent_id_or_slug: UUID|str|None, archived: ArchivedFilter, pages: PagesInput) -> PagesResult[NotesCollection]:
        statement = select(NotesCollection)
        if isinstance(parent_id_or_slug, str):
            statement = statement.where(NotesCollection.parent.has(slug=parent_id_or_slug))
        else:
            statement = statement.where(NotesCollection.parent_id == parent_id_or_slug)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        statement = archived.filter(statement)
        return pages.of(self.session, statement)

    @mutation()
    def create(self, name: str, parent_id_or_slug: UUID|str|None, view: CollectionView = CollectionView.NOTES) -> NotesCollection:
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
    
    @query()
    def get(self, id_or_slug: UUID|str) -> NotesCollection:
        statement = select(NotesCollection)
        if isinstance(id_or_slug, str):
            statement = statement.where(NotesCollection.slug == id_or_slug)
        else:
            statement = statement.where(NotesCollection.id == id_or_slug)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        return self.session.scalars(statement).one()

    @mutation()
    def delete(self, id_or_slug: UUID|str) -> SuccessResult:
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
    def rename(self, id_or_slug: UUID|str, name: str) -> NotesCollection:
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
    def set_archived(self, id_or_slug: UUID|str, archived: bool) -> NotesCollection:
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
    def reparent(self, id_or_slug: UUID|str, parent_id_or_slug: UUID|str|None) -> NotesCollection:
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
