import alembic.command
import alembic.config
import logging
import os
import shutil
from sqlalchemy.sql import text as sql_text

from .database import Database, Model
from ..context import DataContext

logger = logging.getLogger(__name__)


class Migrations:
    MIGRATIONS_PATH = "./migrations"

    context: DataContext
    database: Database
    config: alembic.config.Config

    def __init__(self, context: DataContext):
        self.context = context
        self.database = Database(self.context, wipe_settings=False)
        self._update_ini()
        self.config = alembic.config.Config(self.ini_path)

    @property
    def ini_path(self):
        return os.path.join(self.context.env.temp_path, "migrations.ini")
    
    def _update_ini(self):
        if os.path.isfile(self.ini_path):
            os.remove(self.ini_path)
        with open(self.ini_path, "wt") as fh:
            fh.write("\n".join([
                "[alembic]",
                "file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d_%%(minute).2d_%%(rev)s_%%(slug)s",
                "script_location = migrations",
                "prepend_sys_path = .",
                "version_path_separator = os",
                "sqlalchemy.url = " + self.database.connection_string,
                "[loggers]",
                "keys = root,sqlalchemy,alembic",
                "[handlers]",
                "keys = console",
                "[formatters]",
                "keys = generic",
                "[logger_root]",
                "level = WARN",
                "handlers = console",
                "qualname =",
                "[logger_sqlalchemy]",
                "level = WARN",
                "handlers =",
                "qualname = sqlalchemy.engine",
                "[logger_alembic]",
                "level = INFO",
                "handlers =",
                "qualname = alembic",
                "[handler_console]",
                "class = StreamHandler",
                "args = (sys.stderr,)",
                "level = NOTSET",
                "formatter = generic",
                "[formatter_generic]",
                "format = %(levelname)-5.5s [%(name)s] %(message)s",
                "datefmt = %H:%M:%S",
            ]))

    def init(self):
        logger.info("Initializing migrations")
        alembic.command.init(self.config, self.MIGRATIONS_PATH)
        # automatically edit ./migrations/env.py
        env_py_path = "./migrations/env.py"
        with open(env_py_path, "rt") as envf:
            env_py_code = envf.read()
        env_py_code = env_py_code.replace(
            "target_metadata = None",
            "from core.data.sql.database import Model\n" +
            "target_metadata = Model.metadata")
        with open(env_py_path, "wt") as envf:
            envf.write(env_py_code)
        # delete unnecessary README
        readme_path = "./migrations/README"
        if os.path.isfile(readme_path):
            os.remove(readme_path)

    def new(self, title: str):
        logger.info("Creating new migration")
        alembic.command.revision(self.config, title, True)

    def update(self):
        logger.info("Updating database")
        alembic.command.upgrade(self.config, "head")

    def uninstall(self):
        logger.info("Uninstalling migrations")
        if self.context.env.production:
            logger.critical("Cannot uninstall the database in production mode")
            raise Exception("Cannot uninstall the database in production mode")
        # drop all tables
        tables = Model.metadata.sorted_tables
        logger.info("Will empty %s tables", len(tables))
        with self.database.make_session() as session:
            session.execute(sql_text("SET foreign_key_checks = 0;"))
            statement = "\n".join([f"TRUNCATE `{t.name}`;" for t in tables])
            session.execute(sql_text(statement))
            session.execute(sql_text("SET foreign_key_checks = 1;"))
            # remove all local file data
            temp_path: str = self.context.env.temp_path
            appdata_path = self.context.env.appdata_path
            if os.path.isdir(temp_path):
                logger.info("Deleting temporary directory '%s'", temp_path)
                shutil.rmtree(temp_path)
            if os.path.isdir(appdata_path):
                logger.info("Deleting application data directory '%s'", appdata_path)
                shutil.rmtree(appdata_path)
