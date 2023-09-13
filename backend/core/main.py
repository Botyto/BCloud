import atexit
from datetime import timedelta
import logging
import sys
from typing import cast

from .env import Environment
from .context import BaseContext
from .logging import clear_old_logs, default_setup as setup_logging

from .app.main import AppContext, App
from .data.blobs.fs import FsBlobManager
from .data.context import BlobsSettings, SqlSettings, DataContext
from .data.sql.migrations import MigrationAction, MigrationsManager

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
        host=cast(str, env.get("DB_HOST")),
        port=cast(int, env.get("DB_PORT", 3306)),
        username=cast(str, env.get("DB_USERNAME")),
        password=cast(str, env.get("DB_PASSWORD")),
        database=cast(str, env.get("DB_DATABASE", "")),
    )
    blobs_manager = FsBlobManager(".")
    blobs_settings = BlobsSettings(blobs_manager)
    context = BaseContext(env)
    context = DataContext(context, sql_settings, blobs_settings)
    context = AppContext(context)
    app = App(context)
    app.run()

def run_migration(action: MigrationAction):
    sql_settings = SqlSettings(
        host=cast(str, env.get("DB_HOST")),
        port=cast(int, env.get("DB_PORT", 3306)),
        username=cast(str, env.get("DB_ADMIN_USERNAME", env.get("DB_USERNAME"))),
        password=cast(str, env.get("DB_ADMIN_PASSWORD", env.get("DB_PASSWORD"))),
        database=cast(str, env.get("DB_DATABASE", "")),
    )
    blobs_manager = FsBlobManager(".")
    blobs_settings = BlobsSettings(blobs_manager)
    context = BaseContext(env)
    context = DataContext(context, sql_settings, blobs_settings)
    manager = MigrationsManager()
    match action:
        case MigrationAction.INIT:
            manager.init()
        case MigrationAction.NEW:
            manager.new()
        case MigrationAction.UPDATE:
            manager.update()
        case MigrationAction.UNINSTALL:
            manager.uninstall()
