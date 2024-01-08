from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from core.data.sql.columns import ensure_str_fit

from ..data import NotesCollection, NotesCollectionView


class CollectionsManager:
    user_id: UUID|None
    session: Session
    service: bool

    def __init__(self, user_id: UUID|None, session: Session, service: bool = False):
        self.user_id = user_id
        self.session = session
        self.service = service
    
    @classmethod
    def for_service(cls, user_id: UUID|None, session: Session):
        return cls(user_id, session, service=True)
    
    def get(self, id_or_slug: UUID|str):
        statement = select(NotesCollection)
        if isinstance(id_or_slug, str):
            statement = statement.where(NotesCollection.slug == id_or_slug)
        else:
            statement = statement.where(NotesCollection.id == id_or_slug)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        return self.session.scalars(statement).one_or_none()

    def by_name(self, name: str, root: bool) -> NotesCollection|None:
        statement = select(NotesCollection) \
            .where(NotesCollection.name == name)
        if root:
            statement = statement.where(NotesCollection.parent_id == None)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        return self.session.scalars(statement).first()
    
    def create(self, name: str, parent_id_or_slug: UUID|str|None, view: NotesCollectionView) -> NotesCollection:
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
        return collection
    
    def delete(self, id_or_slug: UUID|str):
        statement = delete(NotesCollection) \
            .returning(NotesCollection.id, NotesCollection.name)
        if isinstance(id_or_slug, str):
            statement = statement.where(NotesCollection.slug == id_or_slug)
        else:
            statement = statement.where(NotesCollection.id == id_or_slug)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        result = self.session.execute(statement)
        id, name = result.scalar_one()
        return id, name
    
    def rename(self, id_or_slug: UUID|str, name: str):
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
        return old_name, collection
    
    def set_archived(self, id_or_slug: UUID|str, archived: bool):
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
        return collection
    
    def reparent(self, id_or_slug: UUID|str, parent_id_or_slug: UUID|str|None):
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
        return old_parent_id, collection
