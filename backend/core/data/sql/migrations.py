from enum import Enum


class MigrationAction(Enum):
    INIT = "init"
    NEW = "new"
    UPDATE = "update"
    UNINSTALL = "uninstall"


class MigrationsManager:
    def init(self):
        pass

    def new(self):
        pass

    def update(self):
        pass

    def uninstall(self):
        pass
