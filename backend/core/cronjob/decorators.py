import asyncio
import functools
import threading
import typing

from .constants import ANY, RANDOM, MONDAY
from .engine import engine
from .schedule import Schedule

def _register(fn, schedule):
    engine.register(fn, schedule)

def in_thread(fn):
    @functools.wraps(fn)
    def fn_in_thread(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return fn_in_thread

def with_async_loop(fn):
    @functools.wraps(fn)
    def fn_in_asyncio_loop(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        fn(loop, *args, **kwargs)
        loop.close()
    return fn_in_asyncio_loop

def job(
    minute: int|range|str|typing.List[int|range|str] = ANY,
    hour: int|range|str|typing.List[int|range|str] = ANY,
    day_of_month: int|range|str|typing.List[int|range|str] = ANY,
    month: int|range|str|typing.List[int|range|str] = ANY,
    day_of_week: int|range|str|typing.List[int|range|str] = ANY,
):
    def decorator(fn):
        _register(fn, Schedule(minute, hour, day_of_month, month, day_of_week))
        return fn
    return decorator

def minutely():
    def decorator(fn):
        _register(fn, Schedule())
        return fn
    return decorator

def hourly(minute: int|str = RANDOM):
    def decorator(fn):
        _register(fn, Schedule(minute=minute))
        return fn
    return decorator

def daily(hour: int|str = RANDOM):
    def decorator(fn):
        _register(fn, Schedule(minute=0, hour=hour))
        return fn
    return decorator

def weekly(day_of_week: int = MONDAY):
    def decorator(fn):
        _register(fn, Schedule(minute=0, hour=0, day_of_week=day_of_week))
        return fn
    return decorator

def monthly(day_of_month: int = 1):
    def decorator(fn):
        _register(fn, Schedule(minute=0, hour=0, day_of_month=day_of_month))
        return fn
    return decorator

def yearly(month: int = 1):
    def decorator(fn):
        _register(fn, Schedule(minute=0, hour=0, day_of_month=1, month=month))
        return fn
    return decorator
