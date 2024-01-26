import asyncio
import logging
import os
import time
from typing import cast

from ..app.main import AppContext, App
from ..asyncjob.context import AsyncJobContext
from ..asyncjob.engine import AsyncJobs
from ..context import BaseContext
from ..cronjob.engine import Scheduler
from ..data.blobs.settings import BlobSettings
from ..data.context import SqlSettings, DataContext
from ..data.sql.database import Database
from ..env import Environment
from ..miniapp.context import MiniappContext
from ..miniapp.engine import Manager as MiniappsManager
from ..msg import Messages

logger = logging.getLogger(__name__)

def load_miniapps(context: MiniappContext):
    from ..api.gql import GraphQLMiniapp
    from miniapps.profile.app import ProfileMiniapp
    from miniapps.files.app import FilesMiniapp
    from miniapps.notes.app import NotesMiniapp
    from miniapps.photos.app import PhotosMiniapp
    logger.info(f"Miniapp load time: %.3fs", time.time() - context.miniapp_init_time)
    return [
        GraphQLMiniapp,
        ProfileMiniapp,
        FilesMiniapp,
        NotesMiniapp,
        PhotosMiniapp,
    ]

def build_manager(env: Environment, context: BaseContext):
    sql_settings = SqlSettings(
        cast(str, env.get("DB_CONNECTION", "sqlite:///./data.db")),
    )
    blob_settings = BlobSettings(
        fs_root=os.path.abspath(cast(str, env.get("BLOB_FS_ROOT"))),
        sql_conn_str=cast(str, env.get("BLOB_SQL"))
    )
    context = DataContext(context, sql_settings, blob_settings)

    database = Database(context)
    msg = Messages()
    cron = Scheduler(asyncio.get_event_loop())
    blobs = blob_settings.build()
    context = AsyncJobContext(context, database, blobs, msg, cron)

    asyncjobs = AsyncJobs(context)
    context = MiniappContext(context, asyncjobs)

    miniapp_types = load_miniapps(context)
    
    miniapps = MiniappsManager(context)
    for miniapp_type in miniapp_types:
        miniapps.register(miniapp_type())

    return miniapps

def run_app(env: Environment, context: BaseContext):
    miniapps = build_manager(env, context)
    context = AppContext(miniapps.context, miniapps)
    app = App(context)
    app.run()
