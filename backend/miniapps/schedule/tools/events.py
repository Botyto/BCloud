from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.data.sql.columns import ensure_str_fit

from ..data import ScheduleCalendar, ScheduleEvent

from .calendars import CalendarManager
from .repetition import get_repetitions
from .sql_helper import copy_columns


class EventOccurance:
    event: ScheduleEvent
    datetime_from: datetime

    def __init__(self, event: ScheduleEvent, datetime_from: datetime):
        self.event = event
        self.datetime_from = datetime_from

    @property
    def event_id(self) -> UUID:
        return self.event.id

    @property
    def datetime_to(self) -> datetime:
        return self.datetime_from + (self.event.datetime_to_utc - self.event.datetime_from_utc)

    @property
    def is_all_day(self) -> bool:
        return self.event.is_all_day


class EventManager:
    user_id: UUID|None
    session: Session
    service: bool
    _calendars: CalendarManager|None = None

    @property
    def calendars(self) -> CalendarManager:
        if self._calendars is None:
            self._calendars = CalendarManager(self.user_id, self.session, self.service)
        return self._calendars

    def __init__(self, user_id: UUID|None, session: Session, service: bool = False):
        self.user_id = user_id
        self.session = session
        self.service = service
    
    @classmethod
    def for_service(cls, user_id: UUID|None, session: Session):
        return cls(user_id, session, service=True)
    
    def get(self, id: UUID):
        statement = select(ScheduleEvent) \
            .where(ScheduleEvent.id == id)
        if self.user_id is not None:
            statement = statement.where(ScheduleEvent.calendar.has(ScheduleCalendar.user_id == self.user_id))
        return self.session.scalars(statement).one_or_none()

    def by_range(self, calendar_id_or_slug: UUID|str|None, start: datetime, end: datetime):
        if start.tzinfo is None:
            raise ValueError("Start datetime must have timezone")
        if end.tzinfo is None:
            raise ValueError("End datetime must have timezone")
        start = start.astimezone(timezone.utc)
        end = end.astimezone(timezone.utc)
        statement = select(ScheduleEvent) \
            .where(ScheduleEvent.first_reminder_datetime_utc <= end) \
            .where(ScheduleEvent.last_occurance_datetime_to_utc >= start)
        if calendar_id_or_slug is not None:
            if isinstance(calendar_id_or_slug, UUID):
                statement = statement.where(ScheduleEvent.calendar_id == calendar_id_or_slug)
            else:
                statement = statement.where(ScheduleEvent.calendar.has(ScheduleCalendar.slug == calendar_id_or_slug))
        if self.user_id is not None:
            statement = statement.where(ScheduleEvent.calendar.has(ScheduleCalendar.user_id == self.user_id))
        events = self.session.scalars(statement).all()
        occurances: List[EventOccurance] = []
        for event in events:
            all_starts = get_repetitions(
                first=event.datetime_from_utc,
                period=event.repeat_period,
                interval=event.repeat_interval,
                weekdays_mask=event.repeat_weekdays_mask,
                until=event.repeat_until_utc,
                end_after=event.repeat_end_after,
                start=start,
                end=end)
            occurances.extend(EventOccurance(event, event_start) for event_start in all_starts)
        return events, occurances
    
    def create(self, calendar_id_or_slug: UUID|str, event: ScheduleEvent) -> ScheduleEvent:
        ensure_str_fit("name", event.name, ScheduleEvent.name)
        ensure_str_fit("description", event.description, ScheduleEvent.description)
        calendar = self.calendars.get(calendar_id_or_slug)
        if calendar is None:
            raise ValueError(f"Calendar '{calendar_id_or_slug}' not found")
        event.calendar = calendar
        event.calendar_id = calendar.id
        event.name = event.name
        event.description = event.description
        self.session.add(event)
        return event
    
    def delete(self, id: UUID) -> ScheduleEvent:
        event = self.get(id)
        if event is None:
            raise ValueError(f"Event '{id}' not found")
        self.session.delete(event)
        return event
    
    def update(self, id: UUID, event: ScheduleEvent) -> ScheduleEvent:
        ensure_str_fit("name", event.name, ScheduleEvent.name)
        ensure_str_fit("description", event.description, ScheduleEvent.description)
        original_event = self.get(id)
        if original_event is None:
            raise ValueError(f"Event '{id}' not found")
        copy_columns(event, original_event, exclude=[
                "calendar_id", "calendar",
                "first_reminder_datetime_utc",
                "last_occurance_datetime_to_utc",
        ])
        return original_event
