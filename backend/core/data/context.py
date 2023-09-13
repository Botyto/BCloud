from dataclasses import dataclass

from core.context import BaseContext


@dataclass
class SqlSettings:
    host: str
    port: int
    username: str
    password: str
    database: str = "bcloud"


class DataContext(BaseContext):
    sql: SqlSettings
