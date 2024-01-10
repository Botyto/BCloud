from uuid import UUID

from core.asyncjob.context import AsyncJobContext
from core.data.sql.database import Session


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
