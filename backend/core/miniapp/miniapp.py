from dataclasses import dataclass
from typing import Callable, Dict, List, Type

from .context import MiniappContext
from .data import MiniappVersion

from ..asyncjob.handlers import HandlerType
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


@dataclass
class MiniappAsyncJob:
    type: str
    handler: HandlerType


class Miniapp:
    id: str
    start_fn: LifetimeFunc|None
    stop_fn: LifetimeFunc|None
    modules_types: List[Type[MiniappModule]]|None
    async_jobs: List[MiniappAsyncJob]|None
    update_fns: Dict[int, UpdateFunc]|None
    mandatory: bool
    dependencies: List[str]|None

    def __init__(
        self,
        id: str, *,
        start: LifetimeFunc|None = None,
        stop: LifetimeFunc|None = None,
        module_types: List[Type[MiniappModule]]|None = None,
        async_jobs: List[MiniappAsyncJob]|None = None,
        update_fns: Dict[int, UpdateFunc]|None = None,
        mandatory: bool = True,
        dependencies: List[str]|None = None,
    ):
        assert id, "App ID cannot be empty"
        assert ensure_str_fit("App ID", id, MiniappVersion.id)
        self.id = id
        self.start_fn = start
        self.stop_fn = stop
        self.modules_types = module_types
        self.async_jobs = async_jobs
        self.update_fns = update_fns
        self.mandatory = mandatory
        self.dependencies = dependencies

    def start(self, context: MiniappContext):
        if self.start_fn is not None:
            self.start_fn(context)
        if self.modules_types is not None:
            for module_type in self.modules_types:
                module_type.start(self, context)
        if self.async_jobs is not None:
            for async_job in self.async_jobs:
                context.asyncjobs.handlers.add(self.id, async_job.type, async_job.handler)

    def update(self, context: MiniappContext):
        if self.update_fns is not None:
            for update_fn in self.update_fns.values():
                update_fn(context)
