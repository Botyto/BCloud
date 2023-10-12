from typing import Type, TYPE_CHECKING

from .context import MiniappContext
from .registry import MiniappRegistry

if TYPE_CHECKING:
    from .miniapp import Miniapp


class MiniappModule:
    miniapp: "Miniapp"
    context: MiniappContext

    def __init__(self, miniapp: "Miniapp", context: MiniappContext):
        self.miniapp = miniapp
        self.context = context

    @classmethod
    def start(cls, miniapp: "Miniapp", context: MiniappContext):
        pass


class ModuleRegistry(MiniappRegistry):
    module_type: Type[MiniappModule]

    def __init__(self, module_type: Type[MiniappModule]):
        self.module_type = module_type

    def start(self, miniapp: Miniapp, context: MiniappContext):
        self.module_type.start(miniapp, context)
