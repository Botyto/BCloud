from enum import Enum
from typing import cast

from ..context import BaseContext
from ..env import Environment
from ..data.blobs.settings import BlobSettings
from ..data.context import SqlSettings, DataContext
from ..data.sql.migrations import Migrations

from .server import load_miniapps


class MigrationAction(Enum):
    INIT = "init"
    NEW = "new"
    UPDATE = "update"
    UNINSTALL = "uninstall"

def run_migration(env: Environment, context: BaseContext, action: MigrationAction, title: str|None = None):
    sql_settings = SqlSettings(
        cast(str, env.get("DB_ADMIN_CONNECTION", "sqlite:///./data.db")),
    )
    blob_settings = BlobSettings(
        fs_root=cast(str, env.get("BLOB_FS_ROOT", ".")),
        sql_conn_str=cast(str, env.get("BLOB_SQL")),
    )
    context = DataContext(context, sql_settings, blob_settings)
    load_miniapps()
    manager = Migrations(context)
    match action:
        case MigrationAction.INIT:
            manager.init()
        case MigrationAction.NEW:
            assert title is not None, "Missing migration title"
            manager.new(title)
        case MigrationAction.UPDATE:
            manager.update()
        case MigrationAction.UNINSTALL:
            manager.uninstall()
