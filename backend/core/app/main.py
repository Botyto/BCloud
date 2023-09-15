import logging

from . import pref

from ..data.blobs.base import Blobs
from ..data.context import DataContext
from ..data.sql.database import Database

logger = logging.getLogger(__name__)


class AppContext(DataContext):
    database: Database
    files: Blobs

    def __init__(self, base: DataContext, database: Database, files: Blobs):
        self._extend(base)
        self.database = database
        self.files = files


class App:
    context: AppContext

    def __init__(self, context: AppContext):
        self.context = context

    def run(self):
        from core.data.blobs.base import Address
        address = Address.unique(self.context.files, "app")
        self.context.files.write(address, b"Hello, world!")
        with self.context.database.make_session() as session:
            preferences = pref.Preferences(session)
            preferences.set("test", "test_value")
            logger.info("Preferences: %s", preferences.get_dict())
        logger.info("Running app...")
