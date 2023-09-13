from enum import Enum

from ..context import DataContext


class MigrationAction(Enum):
    INIT = "init"
    NEW = "new"
    UPDATE = "update"
    UNINSTALL = "uninstall"


class MigrationsManager:
    context: DataContext

    def __init__(self, context: DataContext):
        self.context = context

    def init(self):
        pass

    def new(self):
        pass

    def update(self):
        pass

    def uninstall(self):
        pass
