import sqlalchemy.event
from typing import Type, TYPE_CHECKING

from .context import MiniappContext
from .registry import MiniappRegistry

if TYPE_CHECKING:
    from .miniapp import Miniapp


class MiniappSqlEvent:
    TARGET: Type
    IDENTIFIER: str

    miniapp: "Miniapp"
    context: MiniappContext

    def __init__(self, miniapp: "Miniapp", context: MiniappContext):
        self.miniapp = miniapp
        self.context = context

    def run(self, *args, **kwargs):
        raise NotImplementedError()


class SqlEventRegistry(MiniappRegistry):
    handler_type: Type[MiniappSqlEvent]

    def __init__(self, handler_type: Type[MiniappSqlEvent]):
        self.handler_type = handler_type

    def start(self, miniapp: "Miniapp", context: MiniappContext):
        def wrapper(*args, **kwargs):
            handler = self.handler_type(miniapp, context)
            return handler.run(*args, **kwargs)
        target = self.handler_type.TARGET
        identifier = self.handler_type.IDENTIFIER
        sqlalchemy.event.listen(target, identifier, wrapper)
        # TODO remove listener on stop
