from datetime import datetime
import random
from typing import List

from .constants import ANY, RANDOM, JANUARY, DECEMBER, MONDAY, SUNDAY, EVEN, ODD


ScheduleParam = int|range|str|List[int|range|str]


class Schedule:
    minute: List[range]
    hour: List[range]
    day_of_month: List[range]
    month: List[range]
    day_of_week: List[range]

    def __init__(self,
        minute: ScheduleParam = ANY,
        hour: ScheduleParam = ANY,
        day_of_month: ScheduleParam = ANY,
        month: ScheduleParam = ANY,
        day_of_week: ScheduleParam = ANY,
    ):
        self.minute = self._transform_param("minute", minute, 0, 59)
        self.hour = self._transform_param("hour", hour, 0, 23)
        self.day_of_month = self._transform_param("day_of_month", day_of_month, 1, 31)
        self.month = self._transform_param("month", month, JANUARY, DECEMBER)
        self.day_of_week = self._transform_param("day_of_week", day_of_week, MONDAY, SUNDAY)

    def _transform_param_single(self, name, arg: ScheduleParam, min: int, max: int):
        result: range|None = None
        assert not isinstance(arg, list), f"Cronjob param `{name}` cannot be a nested list"
        if isinstance(arg, str):
            if arg == ANY:
                result = range(min, max + 1)
            elif arg == RANDOM:
                value = random.randint(min, max - 1)
                result = range(value, value + 1)
            elif arg == EVEN:
                result = range(min, max + 1, 2)
            elif arg == ODD:
                result = range(min + 1, max + 1, 2)
        elif isinstance(arg, int):
            if min > arg or arg > max:
                raise ValueError(f"Invalid cronjob param `{name}`: must be between {min} and {max}")
            result = range(arg, arg + 1)
        elif isinstance(arg, range):
            if min > arg.start or arg.stop > max:
                raise ValueError(f"Invalid cronjob param `{name}`: must be between {min} and {max}")
            result = arg
        if result is not None:
            return result
        raise ValueError("Invalid cronjob paramter for `{name}`")
        
    def _transform_param(self, name, arg: ScheduleParam, min: int, max: int):
        if not isinstance(arg, list):
            arg = [arg]
        return [self._transform_param_single(name, item, min, max) for item in arg]

    def match(self, now: datetime):
        for minute_range in self.minute:
            if now.minute not in minute_range:
                return False
        for hour_range in self.hour:
            if now.hour not in hour_range:
                return False
        for day_of_month_range in self.day_of_month:
            if now.day not in day_of_month_range:
                return False
        for month_range in self.month:
            if now.month not in month_range:
                return False
        for day_of_week_range in self.day_of_week:
            if now.weekday() not in day_of_week_range:
                return False
        return True
    
    @classmethod
    def minutely(cls):
        return cls()
    
    @classmethod
    def hourly(cls, minute: int|str = RANDOM):
        return cls(minute=minute)
    
    @classmethod
    def daily(cls, hour: int|str = RANDOM):
        return cls(minute=0, hour=hour)
    
    @classmethod
    def weekly(cls, day_of_week: int = MONDAY):
        return cls(minute=0, hour=0, day_of_week=day_of_week)
    
    @classmethod
    def monthly(cls, day_of_month: int = 1):
        return cls(minute=0, hour=0, day_of_month=day_of_month)

    @classmethod
    def yearly(cls, month: int = 1):
        return cls(minute=0, hour=0, day_of_month=1, month=month)
