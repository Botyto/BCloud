import logging

from ..data.blobs.manager import BlobManager
from ..data.context import DataContext
from ..data.sql.database import DatabaseManager

logger = logging.getLogger(__name__)

from . import pref

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
        address = Address.unique(self.context.files, "app")
        self.context.files.write(address, b"Hello, world!")
        with self.context.database.make_session() as session:
            preferences = pref.PreferencesManager(session)
            preferences.set("test", "test_value")
            logger.info("Preferences: %s", preferences.get_dict())
        logger.info("Running app...")
