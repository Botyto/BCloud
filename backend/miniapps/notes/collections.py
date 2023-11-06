from sqlalchemy import delete, select

from core.api.modules.gql import GqlMiniappModule, query, mutation
from core.api.pages import PagesInput, PagesResult
from core.data.sql.columns import ensure_str_fit
from core.graphql.result import SuccessResult

from .data import NotesCollection, CollectionView


class CollectionsModule(GqlMiniappModule):
    @query()
    def list(self, parent_id: int|None, pages: PagesInput) -> PagesResult[NotesCollection]:
        statement = select(NotesCollection) \
            .where(NotesCollection.parent_id == parent_id)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        return pages.of(self.session, statement)

    @mutation()
    def create(self, name: str, parent_id: int|None, view: CollectionView = CollectionView.NOTES) -> NotesCollection:
        ensure_str_fit("name", name, NotesCollection.name)
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
    def delete(self, id: int) -> SuccessResult:
        statement = delete(NotesCollection) \
            .where(NotesCollection.id == id) \
            .returning(NotesCollection.name)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        result = self.session.execute(statement)
        name = result.scalar_one()
        self.log_activity("collection.delete", {"id": str(id), "name": name})
        return SuccessResult()

    @mutation()
    def rename(self, id: int, name: str) -> NotesCollection:
        ensure_str_fit("name", name, NotesCollection.name)
        statement = select(NotesCollection) \
            .where(NotesCollection.id == id)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        collection = self.session.scalars(statement).one()
        old_name = collection.name
        collection.name = name
        self.session.commit()
        self.log_activity("collection.rename", {"id": str(id), "new": name, "old": old_name})
        return collection

    @mutation()
    def reparent(self, id: int, parent_id: int|None) -> NotesCollection:
        statement = select(NotesCollection) \
            .where(NotesCollection.id == id)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        collection = self.session.scalars(statement).one()
        old_parent_id = collection.parent_id
        collection.parent_id = parent_id
        self.session.commit()
        self.log_activity("collection.reparent", {"id": str(id), "new": parent_id, "old": old_parent_id})
        return collection
