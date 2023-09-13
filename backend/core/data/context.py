from .blobs.manager import BlobManager
from .sql.settings import SqlSettings

from ..context import BaseContext


class DataContext(BaseContext):
    sql: SqlSettings
    blobs: BlobManager

    def __init__(self, base: BaseContext, sql: SqlSettings, blobs: BlobManager):
        self._extend(base)
        self.sql = sql
        self.blobs = blobs
