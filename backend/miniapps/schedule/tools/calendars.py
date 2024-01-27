from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from core.data.sql.columns import ensure_str_fit

from ..data import ScheduleCalendar


class CalendarManager:
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
        statement = select(ScheduleCalendar)
        if isinstance(id_or_slug, str):
            statement = statement.where(ScheduleCalendar.slug == id_or_slug)
        else:
            statement = statement.where(ScheduleCalendar.id == id_or_slug)
        if self.user_id is not None:
            statement = statement.where(ScheduleCalendar.user_id == self.user_id)
        return self.session.scalars(statement).one_or_none()

    def by_name(self, name: str):
        statement = select(ScheduleCalendar) \
            .where(ScheduleCalendar.name == name)
        if self.user_id is not None:
            statement = statement.where(ScheduleCalendar.user_id == self.user_id)
        return self.session.scalars(statement).first()
    
    def create(self, name: str):
        ensure_str_fit("name", name, ScheduleCalendar.name)
        collection = ScheduleCalendar(
            user_id=self.user_id,
            name=name,
        )
        self.session.add(collection)
        self.session.commit()
        return collection
    
    def delete(self, id_or_slug: UUID|str):
        statement = delete(ScheduleCalendar) \
            .returning(ScheduleCalendar.id, ScheduleCalendar.name)
        if isinstance(id_or_slug, str):
            statement = statement.where(ScheduleCalendar.slug == id_or_slug)
        else:
            statement = statement.where(ScheduleCalendar.id == id_or_slug)
        if self.user_id is not None:
            statement = statement.where(ScheduleCalendar.user_id == self.user_id)
        result = self.session.execute(statement)
        id, name = result.scalar_one()
        return id, name
    
    def rename(self, id_or_slug: UUID|str, name: str):
        ensure_str_fit("name", name, ScheduleCalendar.name)
        statement = select(ScheduleCalendar)
        if isinstance(id_or_slug, str):
            statement = statement.where(ScheduleCalendar.slug == id_or_slug)
        else:
            statement = statement.where(ScheduleCalendar.id == id_or_slug)
        if self.user_id is not None:
            statement = statement.where(ScheduleCalendar.user_id == self.user_id)
        collection = self.session.scalars(statement).one()
        old_name = collection.name
        collection.name = name
        self.session.commit()
        return old_name, collection
