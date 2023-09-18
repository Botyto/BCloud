from ..cronjob.engine import Scheduler
from ..data.context import DataContext
from ..data.sql.database import Database
from ..msg import Messages


class AsyncJobContext(DataContext):
    database: Database
    msg: Messages
    cron: Scheduler

    def __init__(self, base: DataContext, database: Database, msg: Messages, cron: Scheduler):
        self._extend(base)
        self.database = database
        self.msg = msg
        self.cron = cron
