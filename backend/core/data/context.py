from tornado.routing import URLSpec
from typing import List

from .blobs.settings import BlobSettings
from .sql.settings import SqlSettings

from ..context import BaseContext
from ..graphql.schema.methods import MethodCollection


class DataContext(BaseContext):
    sql: SqlSettings
    blobs: BlobSettings
    graphql_methods: MethodCollection
    urlspecs: List[URLSpec]

    def __init__(self, base: BaseContext, sql: SqlSettings, blobs: BlobSettings):
        self._extend(base)
        self.sql = sql
        self.blobs = blobs
        self.graphql_methods = MethodCollection()
        self.urlspecs = []
