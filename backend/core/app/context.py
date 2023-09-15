from ..data.blobs.base import Blobs
from ..data.context import DataContext
from ..data.sql.database import Database


class AppContext(DataContext):
    database: Database
    files: Blobs

    def __init__(self, base: DataContext, database: Database, files: Blobs):
        self._extend(base)
        self.database = database
        self.files = files
