import os
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from .settings import SqlSettings

from ...env import Environment


class Model(DeclarativeBase):
    pass


class DatabaseManager:
    env: Environment
    settings: SqlSettings
    engine: Engine
    _sessionmaker: sessionmaker

    def __init__(self, env: Environment, settings: SqlSettings):
        self.env = env
        self.settings = settings
        self.engine = create_engine(self.connection_string, pool_recycle=1800)
        self._sessionmaker = sessionmaker(bind=self.engine)

    @property
    def connection_string(self):
        db_host = self.settings.host
        if db_host.endswith(".sqlite"):
            sqlite_path = os.path.join("data.sqlite")
            return f"sqlite:///{sqlite_path}"
        else:
            db_name = self.settings.database
            if not db_name:
                db_name = SqlSettings.default_database(self.env.production)
            return f"mariadb://{self.settings.username}:{self.settings.password}@{db_host}/{db_name}?charset=utf8mb4"

    def make_session(self, info: dict|None = None) -> Session:
        return self._sessionmaker(info=info)
