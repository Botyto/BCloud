from .env import Environment
from .context import BaseContext

env = Environment()
base_context = BaseContext(env)

import atexit
from datetime import timedelta
import logging
import os
import sys
from typing import cast, Callable

from .logging import clear_old_logs, default_setup as setup_logging

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

from .entry.server import run_app
from .entry.migrations import MigrationAction, run_migration

def start(method: Callable, *args, **kwargs):
    return method(env, base_context, *args, **kwargs)
