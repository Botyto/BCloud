from uuid import UUID

from sqlalchemy.orm import Session


class NotesManager:
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

    def create(self, collection_id: UUID, title: str, content: str, archived: bool = False):
        raise NotImplementedError()
