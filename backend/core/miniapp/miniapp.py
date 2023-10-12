from typing import Callable, Dict, List

from .context import MiniappContext
from .data import MiniappVersion
from .registry import MiniappRegistry

from .registry import AsyncjobRegistry, MsgRegistry
from .sql import MiniappSqlEvent, SqlEventRegistry
from .module import MiniappModule, ModuleRegistry

from ..data.sql.columns import ensure_str_fit


UpdateFunc = Callable[[MiniappContext], None]


class Miniapp:
    id: str
    registry: List[MiniappRegistry]
    update_fns: Dict[int, UpdateFunc]|None
    mandatory: bool
    dependencies: List[str]|None

    def __init__(
        self,
        id: str,
        *registry: MiniappRegistry,
        update_fns: Dict[int, UpdateFunc]|None = None,
        mandatory: bool = True,
        dependencies: List[str]|None = None,
    ):
        assert id, "App ID cannot be empty"
        assert ensure_str_fit("App ID", id, MiniappVersion.id)
        self.id = id
        self.registry = list(registry)
        self.update_fns = update_fns
        self.mandatory = mandatory
        self.dependencies = dependencies

    def start(self, context: MiniappContext):
        for registry in self.registry:
            registry.start(self, context)
