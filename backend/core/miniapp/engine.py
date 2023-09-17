import logging
from sqlalchemy import select
from typing import Set

from .data import MiniappEnable, MiniappVersion
from .miniapp import Miniapp

from .context import MiniappContext

logger = logging.getLogger(__name__)


class Manager:
    context: MiniappContext
    apps: Set[Miniapp]
    enabled: Set[str]|None

    def __init__(self, context: MiniappContext):
        self.context = context
        self.apps = set()
        self.enabled = None

    def is_present(self, id: str):
        return any(app.id == id for app in self.apps)
    
    @property
    def enabled_apps(self):
        assert self.enabled is not None, "Enabled apps are not fetched"
        return set(app for app in self.apps if app.id in self.enabled)
    
    def get(self, id: str):
        for app in self.apps:
            if app.id == id:
                return app

    def start(self):
        if self.enabled is None:
            self.enabled = self.__fetch_enabled()
        self.__ensure_mandatory_enabled()
        self.__ensure_dependencies_enabled()
        self.__update_apps()
        self.__start_apps()

    def __fetch_enabled(self):
        with self.context.database.make_session() as session:
            statement = select(MiniappEnable)
            enables = session.scalars(statement).all()
            if not enables:
                return set(app.id for app in self.apps)
            return set(enable.id for enable in enables if enable.enabled)
    
    def __ensure_mandatory_enabled(self):
        assert self.enabled is not None, "Enabled apps are not fetched"
        for app in self.apps:
            if app.mandatory and not app.id in self.enabled:
                raise RuntimeError(f"Mandatory miniapp `{app.id}` is not enabled")
    
    def __ensure_dependencies_enabled(self):
        assert self.enabled is not None, "Enabled apps are not fetched"
        for app in self.enabled_apps:
            if not app.dependencies:
                continue
            for dependency in app.dependencies:
                if not dependency in self.enabled:
                    raise RuntimeError(f"Miniapp `{app.id}` depends on `{dependency}`, which is not enabled")

    def __update_apps(self):
        with self.context.database.make_session() as session:
            statement = select(MiniappVersion)
            all_version = session.scalars(statement).all()
            for app in self.enabled_apps:
                versions = list(app.update_fns)
                current: MiniappVersion|None = None
                for version in all_version:
                    if version.id == app.id:
                        current = version
                        break
                if current is None:
                    current = MiniappVersion()
                    current.id = app.id
                    current.version = 0
                    session.add(current)
                versions.sort()
                for version in versions:
                    fn = app.update_fns[version]
                    if version > current.version:
                        logger.info(f"Installing miniapp `{app.id}` v{version}")
                        # TODO catch exceptions and rollback the session
                        fn(self.context)
                        current.version = version
                logger.debug(f"Miniapp `{app.id}` is up to date (v{current.version})")

    def __start_apps(self):
        for app in self.enabled_apps:
            logger.info(f"Starting miniapp `{app.id}`")
            app.start(self.context)
