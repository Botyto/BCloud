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

    def start(self):
        pass


class Miniapp:
    id: str
    _start_fn: LifetimeFunc
    _stop_fn: LifetimeFunc
    modules: List[MiniappModule]
    _update_fns: Dict[int, UpdateFunc]
    mandatory: bool
    dependencies: List[str]|None

    def __init__(
        self,
        id: str,
        start: LifetimeFunc,
        stop: LifetimeFunc,
        modules: List[MiniappModule],
        update_fns: Dict[int, UpdateFunc],
        mandatory: bool,
        dependencies: List[str]|None,
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
        self._start_fn(context)
        for module in self.modules:
            module.start()

    def update(self, context: MiniappContext):
        for update_fn in self._update_fns.values():
            update_fn(context)
