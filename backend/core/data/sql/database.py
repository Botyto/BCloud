from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine, Engine, event, DateTime, Column
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from typing import List

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
        def dbg_print_connect(dbapi_con, connection_record):
            logger.debug("Connecting to database: %s", dbapi_con)
        event.listen(self.engine, "connect", dbg_print_connect)
        
        def dbg_print_disconnect(dbapi_con, connection_record):
            logger.debug("Disconnecting from database: %s", dbapi_con)
        event.listen(self.engine, "detach", dbg_print_disconnect)

        def dbg_print_sql(conn, clauseelement, multiparams, params, execution_options):
            sql = str(clauseelement).replace("\n", " ")
            logger.debug("Executing SQL: %s", sql)
        event.listen(self.engine, "before_execute", dbg_print_sql)

        def dbg_datetime_asserts(mapper, cls):
            cls_name = cls.__name__
            columns: List[Column] = cls.__table__.columns
            for column in columns:
                if not isinstance(column.type, DateTime):
                    continue
                assert column.name.endswith("_utc"), f"DateTime column {cls_name}.{column.name} must end with _utc"
        event.listen(Model, "instrument_class", dbg_datetime_asserts, propagate=True)

        for cls in Model.__subclasses__():
            table_name = getattr(cls, "__tablename__", getattr(cls, "__table__"))
            assert table_name == cls.__name__, "Table name must be the same as the model class name"

def apply_timezone_guard(mapper, cls):
    cls_name = cls.__name__
    columns: List[Column] = cls.__table__.columns
    for column in columns:
        if not isinstance(column.type, DateTime):
            continue
        def guarded_set(target, value, oldvalue, initiator):
            if not isinstance(value, datetime):
                return value
            if value.tzinfo is None:
                raise ValueError(f"Cannot assign timezone naive datetime to {cls_name}.{column.name}")
            if value.tzinfo != timezone.utc:
                logger.warning("Converting timezone from %s to UTC for %s.%s", value.tzinfo, cls_name, column.name)
                return value.astimezone(timezone.utc)
            return value
        attr = getattr(cls, column.name)
        event.listen(attr, "set", guarded_set, retvalue=True)
event.listen(Model, "instrument_class", apply_timezone_guard, propagate=True)