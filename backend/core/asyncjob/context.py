from typing import Any

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


class AsyncJobRuntimeContext(AsyncJobContext):
    state: State|None
    job_id: int
    payload: dict

    def __init__(self, base: AsyncJobContext, state: State|None, job_id: int, payload: dict):
        self._extend(base)
        self.state = state
        self.job_id = job_id
        self.payload = payload

    def get_payload(self, key: str, default: Any = None):
        return self.payload.get(key, default)
