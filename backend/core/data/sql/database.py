import os
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session


from .settings import SqlSettings

from ..context import DataContext


class Model(DeclarativeBase):
    pass


class DatabaseManager:
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
