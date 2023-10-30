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

LOGS_PATH = "logs"
logs_max_age_days = cast(int|None, env.get("LOG_MAX_AGE_DAYS"))
if logs_max_age_days is not None:
    clear_old_logs(LOGS_PATH, timedelta(days=logs_max_age_days))
log_level = logging.DEBUG if env.debug else logging.INFO
setup_logging(log_level, LOGS_PATH)
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
        cast(str, env.get("DB_CONNECTION", "sqlite:///./data.db")),
    )
    blob_settings = BlobSettings(
        fs_root=os.path.abspath(cast(str, env.get("BLOB_FS_ROOT"))),
        sql_conn_str=cast(str, env.get("BLOB_SQL"))
    )
    context = DataContext(base_context, sql_settings, blob_settings)

    database = Database(context)
    msg = Messages()
    cron = Scheduler(asyncio.get_event_loop())
    files = blob_settings.build_manager()
    context = AsyncJobContext(context, database, files, msg, cron)

    asyncjobs = AsyncJobs(context)
    context = MiniappContext(context, asyncjobs)

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
        cast(str, env.get("DB_ADMIN_CONNECTION", "sqlite:///./data.db")),
    )
    blob_settings = BlobSettings(
        fs_root=cast(str, env.get("BLOB_FS_ROOT", ".")),
        sql_conn_str=cast(str, env.get("BLOB_SQL")),
    )
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
