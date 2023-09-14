from .blobs.settings import BlobSettings
from .sql.settings import SqlSettings

from ..context import BaseContext


class DataContext(BaseContext):
    sql: SqlSettings
    blobs: BlobSettings

    def __init__(self, base: BaseContext, sql: SqlSettings, blobs: BlobSettings):
        self._extend(base)
        self.sql = sql
        self.blobs = blobs
