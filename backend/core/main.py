from .env import Environment
from .context import BaseContext

env = Environment()
base_context = BaseContext(env)

import atexit
import asyncio
from enum import Enum
from datetime import timedelta
import logging
import os
import sys
import time
from typing import cast

from .logging import clear_old_logs, default_setup as setup_logging

from .app.main import AppContext, App
from .asyncjob.context import AsyncJobContext
from .asyncjob.engine import AsyncJobs
from .cronjob.engine import Scheduler
from .data.blobs.settings import BlobSettings
from .data.context import SqlSettings, DataContext
from .data.sql.database import Database
from .data.sql.migrations import Migrations
from .miniapp.context import MiniappContext
from .miniapp.engine import Manager as MiniappsManager
from .msg import Messages

env.add_cmdline(100)
env.add_dotenv(200, ".env", optional=True)
env.add_json(300, "env.json", optional=True)
env.add_os_env(400)

os.makedirs(env.appdata_path, exist_ok=True)
os.makedirs(env.temp_path, exist_ok=True)

clear_old_logs("logs", timedelta(days=1))
log_level = logging.DEBUG if env.debug else logging.INFO
setup_logging(log_level, "logs")
logger = logging.getLogger(__name__)
cmdline_str = " ".join(sys.argv[1:])
if cmdline_str:
    logger.info("Command line: %s", cmdline_str)
logger.info("Startup (profile: %s)", env.profile)
atexit.register(lambda: logger.info("Shutdown"))

def load_miniapps():
    from .api.gql import GraphQLMiniapp
    from miniapps.profile.app import ProfileMiniapp
    from miniapps.files.app import FilesMiniapp
    return [
        GraphQLMiniapp,
        ProfileMiniapp,
        FilesMiniapp,
    ]

def build_app():
    sql_settings = SqlSettings(
        host=cast(str, env.get("DB_HOST", "localhost")),
        port=cast(int, env.get("DB_PORT", 3306)),
        username=cast(str, env.get("DB_USERNAME", "bcloud")),
        password=cast(str, env.get("DB_PASSWORD", "bcloud")),
        database=cast(str, env.get("DB_DATABASE", "bcloud")),
    )
    blob_settings = BlobSettings(cast(str, env.get("BLOB_FS_ROOT", ".")))
    context = DataContext(base_context, sql_settings, blob_settings)

    database = Database(context)
    msg = Messages()
    cron = Scheduler(asyncio.get_event_loop())
    context = AsyncJobContext(context, database, msg, cron)

    files = blob_settings.build_manager()
    asyncjobs = AsyncJobs(context)
    context = MiniappContext(context, files, asyncjobs)

    miniapps = MiniappsManager(context)
    miniapp_types = load_miniapps()
    for miniapp_type in miniapp_types:
        miniapps.register(miniapp_type())
    logger.info(f"Miniapp load time: %.3fs", time.time() - context.miniapp_init_time)

    context = AppContext(context, miniapps)
    return App(context)

def run_app():
    app = build_app()
    app.run()


class MigrationAction(Enum):
    INIT = "init"
    NEW = "new"
    UPDATE = "update"
    UNINSTALL = "uninstall"

def run_migration(action: MigrationAction, title: str|None = None):
    sql_settings = SqlSettings(
        host=cast(str, env.get("DB_HOST", "localhost")),
        port=cast(int, env.get("DB_PORT", 3306)),
        username=cast(str, env.get("DB_ADMIN_USERNAME", env.get("DB_USERNAME", "bcloud"))),
        password=cast(str, env.get("DB_ADMIN_PASSWORD", env.get("DB_PASSWORD", "bcloud"))),
        database=cast(str, env.get("DB_DATABASE", "bcloud")),
    )
    blob_settings = BlobSettings(cast(str, env.get("BLOB_FS_ROOT", ".")))
    context = DataContext(base_context, sql_settings, blob_settings)
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
