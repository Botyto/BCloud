from abc import ABC, abstractmethod
from typing import Callable, Type, TYPE_CHECKING

from .context import MiniappContext

from ..asyncjob.handlers import AsyncJobHandler

if TYPE_CHECKING:
    from .miniapp import Miniapp


class MiniappRegistry(ABC):
    @abstractmethod
    def start(self, miniapp: "Miniapp", context: MiniappContext):
        ...
    

class ClassRegistry(MiniappRegistry):
    def __init__(self, cls: type):
        pass

    def start(self, miniapp: "Miniapp", context: MiniappContext):
        pass



class MsgRegistry(MiniappRegistry):
    msg: str
    handler: Callable

    def __init__(self, msg: str, handler: Callable):
        self.msg = msg
        self.handler = handler

    def start(self, miniapp: "Miniapp", context: MiniappContext):
        context.msg.register(self.msg, self.handler)


class AsyncjobRegistry(MiniappRegistry):
    handler_type: Type[AsyncJobHandler]

    def __init__(self, handler_type: Type[AsyncJobHandler]):
        self.type = type
        self.handler_type = handler_type

    def start(self, miniapp: "Miniapp", context: MiniappContext):
        context.asyncjobs.handlers.add(miniapp.id, self.handler_type.TYPE, self.handler_type)
