from ..data.blobs.base import Blobs
from ..data.context import DataContext
from ..data.sql.database import Database
from ..msg import Messages
from ..cronjob.engine import Scheduler


class AppContext(DataContext):
    database: Database
    files: Blobs
    msg: Messages
    cron: Scheduler

    def __init__(self,
        base: DataContext,
        database: Database,
        files: Blobs,
        msg: Messages,
        cron: Scheduler,
    ):
        self._extend(base)
        self.database = database
        self.files = files
        self.msg = msg
        self.cron = cron
