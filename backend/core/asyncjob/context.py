from ..cronjob.engine import Scheduler
from ..data.context import DataContext
from ..data.sql.database import Database
from ..msg import Messages

from .state import State


class AsyncJobContext(DataContext):
    database: Database
    msg: Messages
    cron: Scheduler

    def __init__(self, base: DataContext, database: Database, msg: Messages, cron: Scheduler):
        self._extend(base)
        self.database = database
        self.msg = msg
        self.cron = cron


class AsyncJobRuntimeContext(AsyncJobContext):
    state: State|None
    job_id: int
    payload: dict|None

    def __init__(self, base: AsyncJobContext, state: State|None, job_id: int, payload: dict|None):
        self._extend(base)
        self.state = state
        self.job_id = job_id
        self.payload = payload
