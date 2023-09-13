import atexit
from datetime import timedelta
import logging

from .context import BaseContext
from .logging import clear_old_logs, default_setup as setup_logging
from .data.context import SqlSettings, DataContext
from .app.main import AppContext, App

clear_old_logs("logs", timedelta(days=1))
setup_logging(logging.DEBUG, "logs")
logger = logging.getLogger(__name__)
logger.info("Startup")
atexit.register(lambda: logger.info("Shutdown"))

context = BaseContext()
sql_settings = SqlSettings("", 0, "", "", "")
context = DataContext.extend(context, sql=sql_settings)
context = AppContext.extend(context)
app = App(context)
app.run()
