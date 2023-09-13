from .sql.settings import SqlSettings

from ..context import BaseContext


class DataContext(BaseContext):
    sql: SqlSettings
