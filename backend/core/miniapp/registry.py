from typing import Callable, Type, TYPE_CHECKING

from .context import MiniappContext

from ..asyncjob.handlers import AsyncJobHandler

if TYPE_CHECKING:
    from .miniapp import Miniapp


class MiniappRegistry:
    def start(self, miniapp: "Miniapp", context: MiniappContext):
        raise NotImplementedError()


class MsgRegistry(MiniappRegistry):
    msg: str
    handler: Callable

    def __init__(self, msg: str, handler: Callable):
        self.msg = msg
        self.handler = handler

    def start(self, miniapp: "Miniapp", context: MiniappContext):
        context.msg.register(self.msg, self.handler)


class AsyncjobRegistry(MiniappRegistry):
    type: str
    handler: Type[AsyncJobHandler]

    def __init__(self, type: str, handler: Type[AsyncJobHandler]):
        self.type = type
        self.handler = handler

    def start(self, miniapp: "Miniapp", context: MiniappContext):
        context.asyncjobs.handlers.add(miniapp.id, self.type, self.handler)
