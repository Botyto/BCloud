from typing import Callable, Dict, List, Type

from .context import MiniappContext
from .data import MiniappVersion

from ..data.sql.columns import ensure_str_fit


LifetimeFunc = Callable[[MiniappContext], None]
UpdateFunc = Callable[[MiniappContext], None]


class MiniappModule:
    miniapp: "Miniapp"
    context: MiniappContext

    def __init__(self, miniapp: "Miniapp", context: MiniappContext):
        self.miniapp = miniapp
        self.context = context

    @classmethod
    def start(cls, miniapp: "Miniapp", context: MiniappContext):
        pass


class Miniapp:
    id: str
    _start_fn: LifetimeFunc|None
    _stop_fn: LifetimeFunc|None
    modules_types: List[Type[MiniappModule]]|None
    _update_fns: Dict[int, UpdateFunc]|None
    mandatory: bool
    dependencies: List[str]|None

    def __init__(
        self,
        id: str, *,
        start: LifetimeFunc|None = None,
        stop: LifetimeFunc|None = None,
        module_types: List[Type[MiniappModule]]|None = None,
        update_fns: Dict[int, UpdateFunc]|None = None,
        mandatory: bool = True,
        dependencies: List[str]|None = None,
    ):
        assert id, "App ID cannot be empty"
        assert ensure_str_fit("App ID", id, MiniappVersion.id)
        self.id = id
        self._start_fn = start
        self._stop_fn = stop
        self.modules_types = module_types
        self._update_fns = update_fns
        self.mandatory = mandatory
        self.dependencies = dependencies

    def start(self, context: MiniappContext):
        if self._start_fn is not None:
            self._start_fn(context)
        if self.modules_types is not None:
            for module_type in self.modules_types:
                module_type.start(self, context)

    def update(self, context: MiniappContext):
        if self._update_fns is not None:
            for update_fn in self._update_fns.values():
                update_fn(context)
