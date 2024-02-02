from datetime import datetime, timedelta
from enum import Enum as PyEnum, IntFlag
from typing import List
from uuid import UUID as PyUUID, uuid4

from core.auth.owner import owner_info
from core.data.sql.columns import ForeignKey, Mapped, mapped_column, relationship, utcnow_tz
from core.data.sql.columns import UUID, String, Enum, Boolean, DateTime, Integer, Interval
from core.data.sql.database import Model
from core.data.sql.slugs import SLUG_LENGTH, slug_info

from core.auth.data import User

from miniapps.files.data import FileMetadata


class ScheduleCalendar(Model):
    __tablename__ = "ScheduleCalendar"
    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    user_id: Mapped[PyUUID] = mapped_column(ForeignKey(User.id), nullable=False, info=owner_info())
    user: Mapped[User] = relationship(User, backref="calendars")
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    slug: Mapped[str] = mapped_column(String(SLUG_LENGTH), nullable=False, info=slug_info())
    color: Mapped[str] = mapped_column(String(32), nullable=False, default="#dddddd")
    events: Mapped[List["ScheduleEvent"]] = relationship("ScheduleEvent", back_populates="calendar")


class ScheduleEventKind(PyEnum):
    EVENT = "EVENT"
    REMINDER = "REMINDER"
    TASK = "TASK"


class ScheduleEventRepeatPeriod(PyEnum):
    NONE = "NONE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class WeekdayMask(IntFlag):
    MONDAY = 1 << 0
    TUESDAY = 1 << 1
    WEDNESDAY = 1 << 2
    THURSDAY = 1 << 3
    FRIDAY = 1 << 4
    SATURDAY = 1 << 5


class ScheduleEvent(Model):
    __tablename__ = "ScheduleEvent"
    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    calendar_id: Mapped[PyUUID] = mapped_column(ForeignKey(ScheduleCalendar.id), nullable=False, info=owner_info())
    calendar: Mapped[ScheduleCalendar] = relationship(ScheduleCalendar, back_populates="events")
    kind: Mapped[ScheduleEventKind] = mapped_column(Enum(ScheduleEventKind), nullable=False, default=ScheduleEventKind.EVENT)
    name: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    description: Mapped[str] = mapped_column(String(4096), nullable=False, default="")
    busy: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    color: Mapped[str] = mapped_column(String(32), nullable=False, default="#dddddd")
    datetime_from_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow_tz)
    datetime_to_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow_tz)
    reminders: Mapped[List["ScheduleEventReminder"]] = relationship("ScheduleEventReminder", back_populates="event")
    attachments: Mapped[List[FileMetadata]] = relationship("ScheduleEventFileAssoc", back_populates="event")
    # repetition
    repeat_period: Mapped[ScheduleEventRepeatPeriod] = mapped_column(Enum(ScheduleEventRepeatPeriod), nullable=False, default=ScheduleEventRepeatPeriod.NONE)
    repeat_interval: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    repeat_weekdays_mask: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    repeat_until_utc: Mapped[datetime|None] = mapped_column(DateTime, nullable=True, default=None)
    repeat_end_after: Mapped[int|None] = mapped_column(Integer, nullable=True, default=None)
    # cache
    first_reminder_datetime_utc: Mapped[datetime|None] = mapped_column(DateTime, nullable=True, default=None)
    last_occurance_datetime_to_utc: Mapped[datetime|None] = mapped_column(DateTime, nullable=True, default=None)

    @property
    def is_all_day(self) -> bool:
        return self.datetime_from_utc.date() != self.datetime_to_utc.date()


class ScheduleEventFileAssoc(Model):
    __tablename__ = "ScheduleEventFileAssoc"
    event_id: Mapped[PyUUID] = mapped_column(ForeignKey(ScheduleEvent.id), primary_key=True)
    event: Mapped[ScheduleEvent] = relationship(ScheduleEvent, back_populates="attachments", lazy="joined")
    file_id: Mapped[PyUUID] = mapped_column(ForeignKey(FileMetadata.id), nullable=False)
    file: Mapped[FileMetadata] = relationship(FileMetadata, backref="calendar_event", lazy="joined", foreign_keys=[file_id])


class ScheduleEventReminder(Model):
    __tablename__ = "ScheduleEventReminder"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[PyUUID] = mapped_column(ForeignKey(ScheduleEvent.id), nullable=False, info=owner_info())
    event: Mapped[ScheduleEvent] = relationship(ScheduleEvent, back_populates="reminders")
    time_ahead: Mapped[timedelta] = mapped_column(Interval, nullable=False, default=timedelta)
