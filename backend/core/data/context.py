from .blobs.settings import BlobsSettings
from .sql.settings import SqlSettings

from ..context import BaseContext


class DataContext(BaseContext):
    sql: SqlSettings
    blobs: BlobsSettings

    def __init__(self, base: BaseContext, sql: SqlSettings, blobs: BlobsSettings):
        self._extend(base)
        self.sql = sql
        self.blobs = blobs
