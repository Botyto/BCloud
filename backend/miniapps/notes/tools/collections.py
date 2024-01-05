from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..data import NotesCollection


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
    
    def by_name(self, name: str) -> NotesCollection|None:
        statement = select(NotesCollection).where(NotesCollection.name == name)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        return self.session.scalars(statement).one_or_none()
    
    def create(self, name: str, parent_id: UUID|None = None) -> NotesCollection:
        raise NotImplementedError()  # TODO test this
        collection = NotesCollection(name=name, user_id=self.user_id, parent_id=parent_id)
        self.session.add(collection)
        return collection
