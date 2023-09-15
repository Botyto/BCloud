from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine, Engine
import sqlalchemy.event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from types import MethodType

from .settings import SqlSettings

from ..context import DataContext

logger = logging.getLogger(__name__)


class Model(DeclarativeBase):
    pass


class Database:
    context: DataContext
    engine: Engine
    _sessionmaker: sessionmaker

    def __init__(self, context: DataContext, wipe_settings: bool = True):
        self.context = context
        self.engine = create_engine(self.connection_string, pool_recycle=1800)
        self._sessionmaker = sessionmaker(bind=self.engine)
        if self.context.sql.is_sqlite:
            Model.metadata.create_all(self.engine)
        if wipe_settings:
            self.context.sql.wipe()
        if self.context.env.debug:
            self._activate_debug()

    @property
    def connection_string(self):
        db_host = self.context.sql.host
        if self.context.sql.is_sqlite:
            return f"sqlite:///{db_host}"
        else:
            db_name = self.context.sql.database
            if not db_name:
                db_name = SqlSettings.default_database(self.context.env.production)
            db_user = self.context.sql.username
            db_pass = self.context.sql.password
            return f"mariadb://{db_user}:{db_pass}@{db_host}/{db_name}?charset=utf8mb4"

    def make_session(self, info: dict|None = None) -> Session:
        return self._sessionmaker(info=info)
    
    def _activate_debug(self):
        def on_connect(dbapi_con, connection_record):
            logger.debug("Connecting to database: %s", dbapi_con)
        sqlalchemy.event.listen(self.engine, "connect", on_connect)
        
        def on_detch(dbapi_con, connection_record):
            logger.debug("Disconnecting from database: %s", dbapi_con)
        sqlalchemy.event.listen(self.engine, "detach", on_detch)

        def on_before_execute(conn, clauseelement, multiparams, params, execution_options):
            sql = str(clauseelement).replace("\n", " ")
            logger.debug("Executing SQL: %s", sql)
        sqlalchemy.event.listen(self.engine, "before_execute", on_before_execute)

        for cls in Model.__subclasses__():
            table_name = getattr(cls, "__tablename__", getattr(cls, "__table__"))
            assert table_name == cls.__name__, "Table name must be the same as the model class name"
