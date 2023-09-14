import atexit
from enum import Enum
from datetime import timedelta
import logging
import sys
from typing import cast

from .env import Environment
from .context import BaseContext
from .logging import clear_old_logs, default_setup as setup_logging

from .app.main import AppContext, App
from .data.blobs.settings import BlobSettings
from .data.context import SqlSettings, DataContext
from .data.sql.database import Database
from .data.sql.migrations import Migrations

env = Environment()
env.add_cmdline(100)
env.add_dotenv(200, ".env", optional=True)
env.add_json(300, "env.json", optional=True)
env.add_os_env(400)

clear_old_logs("logs", timedelta(days=1))
log_level = logging.DEBUG if env.debug else logging.INFO
setup_logging(log_level, "logs")
logger = logging.getLogger(__name__)
cmdline_str = " ".join(sys.argv[1:])
if cmdline_str:
    logger.info("Command line: %s", cmdline_str)
logger.info("Startup (profile: %s)", env.profile)
atexit.register(lambda: logger.info("Shutdown"))

def run_app():
    sql_settings = SqlSettings(
        host=cast(str, env.get("DB_HOST", "localhost")),
        port=cast(int, env.get("DB_PORT", 3306)),
        username=cast(str, env.get("DB_USERNAME", "bcloud")),
        password=cast(str, env.get("DB_PASSWORD", "bcloud")),
        database=cast(str, env.get("DB_DATABASE", "bcloud")),
    )
    blob_settings = BlobSettings(cast(str, env.get("BLOB_FS_ROOT", ".")))
    context = BaseContext(env)
    context = DataContext(context, sql_settings, blob_settings)
    files = blob_settings.build_manager()
    database = Database(context)
    context = AppContext(context, database, files)
    app = App(context)
    app.run()


class MigrationAction(Enum):
    INIT = "init"
    NEW = "new"
    UPDATE = "update"
    UNINSTALL = "uninstall"

def run_migration(action: MigrationAction):
    sql_settings = SqlSettings(
        host=cast(str, env.get("DB_HOST", "localhost")),
        port=cast(int, env.get("DB_PORT", 3306)),
        username=cast(str, env.get("DB_ADMIN_USERNAME", env.get("DB_USERNAME", "bcloud"))),
        password=cast(str, env.get("DB_ADMIN_PASSWORD", env.get("DB_PASSWORD", "bcloud"))),
        database=cast(str, env.get("DB_DATABASE", "bcloud")),
    )
    blob_settings = BlobSettings(cast(str, env.get("BLOB_FS_ROOT", ".")))
    context = BaseContext(env)
    context = DataContext(context, sql_settings, blob_settings)
    manager = Migrations(context)
    match action:
        case MigrationAction.INIT:
            manager.init()
        case MigrationAction.NEW:
            manager.new()
        case MigrationAction.UPDATE:
            manager.update()
        case MigrationAction.UNINSTALL:
            manager.uninstall()
