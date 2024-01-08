import typeguard
from typing import Any, Type, TypeVar

from ..cronjob.engine import Scheduler
from ..data.blobs.base import Blobs
from ..data.context import DataContext
from ..data.sql.database import Database
from ..msg import Messages

from .state import State


class AsyncJobContext(DataContext):
    database: Database
    blobs: Blobs
    msg: Messages
    cron: Scheduler

    def __init__(self, base: DataContext, database: Database, blobs: Blobs, msg: Messages, cron: Scheduler):
        self._extend(base)
        self.database = database
        self.blobs = blobs
        self.msg = msg
        self.cron = cron

T = TypeVar("T")


class AsyncJobRuntimeContext(AsyncJobContext):
    state: State|None
    job_id: int
    payload: dict[str, Any]

    def __init__(self, base: AsyncJobContext, state: State|None, job_id: int, payload: dict):
        self._extend(base)
        self.state = state
        self.job_id = job_id
        self.payload = payload

    def get_payload(self, *keys: str, default: T = None, expected_type: Type[T] = Any) -> T:
        result = self.payload
        for key in keys:
            result = result.get(key)
            if result is None:
                return default
        return typeguard.check_type(result, expected_type)
    