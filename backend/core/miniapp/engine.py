import logging
from sqlalchemy import select, delete
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
    
    def register(self, app: Miniapp):
        self.apps.add(app)
    
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

    def set_enabled(self, id: str, enabled: bool):
        assert self.enabled is not None, "Enabled apps are not fetched"
        miniapp = self.get(id)
        assert miniapp is not None, f"Miniapp `{id}` is not present"
        if enabled:
            if id in self.enabled:
                return
            logger.info(f"Enabling miniapp `{id}` - restart required")
            with self.context.database.make_session() as session:
                enable_obj = MiniappEnable(id=id, enabled=enabled)
                session.add(enable_obj)
        else:
            if id not in self.enabled:
                return
            logger.info(f"Disabling miniapp `{id}` - restart required")
            with self.context.database.make_session() as session:
                statement = delete(MiniappEnable).where(MiniappEnable.id == id)
                session.execute(statement)

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
                if app._update_fns is None:
                    continue
                versions = list(app._update_fns)
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
                    fn = app._update_fns[version]
                    if version > current.version:
                        logger.info(f"Installing miniapp `{app.id}` v{version}")
                        try:
                            fn(self.context)
                        except Exception as e:
                            logger.error(f"Failed to install miniapp `{app.id}` v{version}")
                            logger.exception(e)
                            raise e
                        current.version = version
                logger.debug(f"Miniapp `{app.id}` is up to date (v{current.version})")

    def __start_apps(self):
        for app in self.enabled_apps:
            logger.info(f"Starting miniapp `{app.id}`")
            app.start(self.context)
