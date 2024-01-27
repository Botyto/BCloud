from datetime import datetime, timedelta, timezone

from dateutil.relativedelta import relativedelta

from core.data.sql.database import Session
from core.miniapp.sql import MiniappSqlEvent

from ..data import ScheduleEvent, ScheduleEventRepeatPeriod

def __check_weekday(date: datetime, weekday_mask: int):
    if weekday_mask == 0:
        return True
    return (weekday_mask & (1 << date.weekday())) != 0

def __relativedelta_interval(period: ScheduleEventRepeatPeriod, interval: int):
    match period:
        case ScheduleEventRepeatPeriod.DAILY:
            return relativedelta(days=interval)
        case ScheduleEventRepeatPeriod.WEEKLY:
            return relativedelta(weeks=interval)
        case ScheduleEventRepeatPeriod.MONTHLY:
            return relativedelta(months=interval)
        case ScheduleEventRepeatPeriod.YEARLY:
            return relativedelta(years=interval)
    raise ValueError(f"Invalid period: {period}")

def get_repetitions(
        first: datetime,
        period: ScheduleEventRepeatPeriod,
        interval: int,
        weekdays_mask: int,
        until: datetime|None,
        end_after: int|None,
        start: datetime,
        end: datetime):
    assert first.tzinfo is not None
    assert start.tzinfo is not None
    assert end.tzinfo is not None
    assert until is None or until.tzinfo is not None
    assert end >= start
    if period == ScheduleEventRepeatPeriod.NONE:
        return [first] if first >= start and first <= end else []
    date_interval = __relativedelta_interval(period, interval)
    if end < first or (until is not None and start > until):
        return []
    next, reps = first, 0
    result = []
    while next < start and (end_after is None or reps < end_after):
        next += date_interval
        reps += 1
    while next < end and (until is None or next <= until) and (end_after is None or reps < end_after):
        if period != ScheduleEventRepeatPeriod.WEEKLY or __check_weekday(next, weekdays_mask) or reps == 0:
            result.append(next)
            reps += 1
        next += date_interval
    return result

def is_repetition(
        first: datetime,
        period: ScheduleEventRepeatPeriod,
        interval: int,
        weekdays_mask: int,
        until: datetime|None,
        end_after: int|None,
        target: datetime,
        tolerance: timedelta):
    assert first.tzinfo is not None
    assert target.tzinfo is not None
    assert until is None or until.tzinfo is not None
    if period == ScheduleEventRepeatPeriod.NONE:
        return (target - first) <= tolerance
    if target < first or (until is not None and target > until + tolerance):
        return False
    if period == ScheduleEventRepeatPeriod.WEEKLY and not __check_weekday(target, weekdays_mask):
        return (target - first) <= tolerance
    reps = 0
    next = first
    date_interval = __relativedelta_interval(period, interval)
    while next <= target and (until is None or next <= until) and (end_after is None or reps < end_after):
        if (target - next) <= tolerance:
            return True
        next += date_interval
        reps += 1


class UpdateEventFromToCaches(MiniappSqlEvent):
    TARGET = Session
    IDENTIFIER = "before_flush"
    
    def run(self, session: Session, flush_context, instances):
        def process_entity_list(entities):
            for event in entities:
                if not isinstance(event, ScheduleEvent):
                    continue
                largest_time_ahead = timedelta()
                for reminder in event.reminders:
                    if reminder.time_ahead > largest_time_ahead:
                        largest_time_ahead = reminder.time_ahead
                event.first_reminder_datetime_utc = event.datetime_from_utc - largest_time_ahead
                if event.repeat_period is not None:
                    if event.repeat_period == ScheduleEventRepeatPeriod.NONE:
                        event.last_occurance_datetime_to_utc = event.datetime_to_utc
                    elif event.repeat_until_utc is None and event.repeat_end_after is None:
                        # repeat forever
                        event.last_occurance_datetime_to_utc = datetime.max.replace(tzinfo=timezone.utc)
                    else:
                        match event.repeat_period:
                            case ScheduleEventRepeatPeriod.DAILY:
                                delta = relativedelta(days=1)
                            case ScheduleEventRepeatPeriod.WEEKLY:
                                delta = relativedelta(weeks=1)
                            case ScheduleEventRepeatPeriod.MONTHLY:
                                delta = relativedelta(months=1)
                            case ScheduleEventRepeatPeriod.YEARLY:
                                delta = relativedelta(years=1)
                        event.last_occurance_datetime_to_utc = event.datetime_to_utc
                        if event.repeat_until_utc is not None:
                            repeat_duration = event.repeat_until_utc - event.datetime_from_utc
                            event.last_occurance_datetime_to_utc += repeat_duration - repeat_duration % delta
                        elif event.repeat_end_after is not None:
                            event.last_occurance_datetime_to_utc += delta * event.repeat_end_after
        process_entity_list(session.new)
        process_entity_list(session.dirty)
