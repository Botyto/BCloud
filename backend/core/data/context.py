from tornado.routing import URLSpec
from typing import List

from .blobs.settings import BlobSettings
from .sql.settings import SqlSettings

from ..context import BaseContext
from ..graphql.schema.methods import MethodCollection


class DataContext(BaseContext):
    sql_settings: SqlSettings
    blob_settings: BlobSettings
    graphql_methods: MethodCollection
    urlspecs: List[URLSpec]

    def __init__(self, base: BaseContext, sql: SqlSettings, blobs: BlobSettings):
        self._extend(base)
        self.sql_settings = sql
        self.blob_settings = blobs
        self.graphql_methods = MethodCollection()
        self.urlspecs = []
