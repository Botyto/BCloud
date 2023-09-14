import logging

from ..data.blobs.manager import BlobManager
from ..data.context import DataContext
from ..data.sql.database import DatabaseManager

logger = logging.getLogger(__name__)


class AppContext(DataContext):
    database: DatabaseManager
    files: BlobManager

    def __init__(self, base: DataContext, database: DatabaseManager, files: BlobManager):
        self._extend(base)
        self.database = database
        self.files = files


class App:
    context: AppContext

    def __init__(self, context: AppContext):
        self.context = context

    def run(self):
        from core.data.blobs.manager import Address
        self.context.files.write(Address.random("app"), b"Hello, world!")
        logger.info("Running app...")
