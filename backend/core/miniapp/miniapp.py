from typing import Callable, Dict, List

from .context import MiniappContext
from .data import MiniappVersion

from ..data.sql.columns import ensure_str_fit


LifetimeFunc = Callable[[MiniappContext], None]
UpdateFunc = Callable[[MiniappContext], None]


class MiniappModule:
    miniapp: "Miniapp"

    def __init__(self, miniapp: "Miniapp"):
        self.miniapp = miniapp

    def start(self, context: MiniappContext):
        pass


class Miniapp:
    id: str
    _start_fn: LifetimeFunc|None
    _stop_fn: LifetimeFunc|None
    modules: List[MiniappModule]|None
    _update_fns: Dict[int, UpdateFunc]|None
    mandatory: bool
    dependencies: List[str]|None

    def __init__(
        self,
        id: str, *,
        start: LifetimeFunc|None = None,
        stop: LifetimeFunc|None = None,
        modules: List[MiniappModule]|None = None,
        update_fns: Dict[int, UpdateFunc]|None = None,
        mandatory: bool = True,
        dependencies: List[str]|None = None,
    ):
        assert id, "App ID cannot be empty"
        assert ensure_str_fit("App ID", id, MiniappVersion.id)
        self.id = id
        self._start_fn = start
        self._stop_fn = stop
        self.modules = modules
        self._update_fns = update_fns
        self.mandatory = mandatory
        self.dependencies = dependencies

    def start(self, context: MiniappContext):
        if self._start_fn is not None:
            self._start_fn(context)
        if self.modules is not None:
            for module in self.modules:
                module.start(context)

    def update(self, context: MiniappContext):
        if self._update_fns is not None:
            for update_fn in self._update_fns.values():
                update_fn(context)
