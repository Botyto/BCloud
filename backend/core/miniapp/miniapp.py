from typing import Callable, Dict, List

from .context import MiniappContext
from .data import MiniappVersion
from .registry import MiniappRegistry

from .registry import AsyncjobRegistry, MsgRegistry
from .sql import MiniappSqlEvent, SqlEventRegistry
from .module import MiniappModule, ModuleRegistry

from ..data.sql.columns import ensure_str_fit


LifetimeFunc = Callable[[MiniappContext], None]
UpdateFunc = Callable[[MiniappContext], None]


class Miniapp:
    id: str
    registry: List[MiniappRegistry]
    start_fn: LifetimeFunc|None
    stop_fn: LifetimeFunc|None
    update_fns: Dict[int, UpdateFunc]|None
    mandatory: bool
    dependencies: List[str]|None

    def __init__(
        self,
        id: str,
        *registry: MiniappRegistry,
        start: LifetimeFunc|None = None,
        stop: LifetimeFunc|None = None,
        update_fns: Dict[int, UpdateFunc]|None = None,
        mandatory: bool = True,
        dependencies: List[str]|None = None,
    ):
        assert id, "App ID cannot be empty"
        assert ensure_str_fit("App ID", id, MiniappVersion.id)
        self.id = id
        self.registry = list(registry)
        self.start_fn = start
        self.stop_fn = stop
        self.update_fns = update_fns
        self.mandatory = mandatory
        self.dependencies = dependencies

    def start(self, context: MiniappContext):
        if self.start_fn is not None:
            self.start_fn(context)
        for registry in self.registry:
            registry.start(self, context)

    def update(self, context: MiniappContext):
        if self.update_fns is not None:
            for update_fn in self.update_fns.values():
                update_fn(context)
