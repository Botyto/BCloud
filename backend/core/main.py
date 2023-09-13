import atexit
from datetime import timedelta
import logging

from .env import Environment
from .context import BaseContext
from .logging import clear_old_logs, default_setup as setup_logging

from .data.context import SqlSettings, DataContext
from .app.main import AppContext, App

env = Environment()
env.add_os_env(100)
env.add_dotenv(200, ".env", optional=True)
env.add_json(300, "env.json", optional=True)

clear_old_logs("logs", timedelta(days=1))
log_level = logging.DEBUG if env.debug else logging.INFO
setup_logging(log_level, "logs")
logger = logging.getLogger(__name__)
logger.info("Startup (profile: %s)", env.profile)
atexit.register(lambda: logger.info("Shutdown"))

context = BaseContext()
sql_settings = SqlSettings("", 0, "", "", "")
context = DataContext.extend(context, sql=sql_settings)
context = AppContext.extend(context)
app = App(context)
app.run()
