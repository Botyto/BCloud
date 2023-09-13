from .sql.settings import SqlSettings

from ..context import BaseContext


class DataContext(BaseContext):
    sql: SqlSettings

    def __init__(self, base: BaseContext, sql: SqlSettings):
        self._extend(base)
        self.sql = sql
