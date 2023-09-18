from typing import Callable, Dict, List

from .context import MiniappContext
from .data import MiniappVersion

from ..data.sql.columns import ensure_str_fit


LifetimeFunc = Callable[[MiniappContext], None]
UpdateFunc = Callable[[MiniappContext], None]


class Miniapp:
    id: str
    start: LifetimeFunc
    stop: LifetimeFunc
    update_fns: Dict[int, UpdateFunc]
    mandatory: bool
    dependencies: List[str]|None

    def __init__(
        self,
        id: str,
        start: LifetimeFunc,
        stop: LifetimeFunc,
        update_fns: Dict[int, UpdateFunc],
        mandatory: bool,
        dependencies: List[str]|None,
    ):
        assert id, "App ID cannot be empty"
        assert ensure_str_fit("App ID", id, MiniappVersion.id)
        self.id = id
        self.start = start
        self.stop = stop
        self.update_fns = update_fns
        self.mandatory = mandatory
        self.dependencies = dependencies
