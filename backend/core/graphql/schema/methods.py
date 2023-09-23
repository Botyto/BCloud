from dataclasses import dataclass
from types import MethodType
from typing import Any, Callable, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..typeinfo import GqlMethodInfo

WrapMethodType = Callable[["GqlMethodInfo"], Any]


@dataclass
class MethodBuildInfo:
    wrap: WrapMethodType
    method: MethodType

    def wrap_method(self, minfo: "GqlMethodInfo"):
        return minfo.wrap()


class MethodCollection:
    queries: List[MethodBuildInfo]
    mutations: List[MethodBuildInfo]
    subscriptions: List[MethodBuildInfo]

    def __init__(self):
        self.queries = []
        self.mutations = []
        self.subscriptions = []

    def register_query(self, wrap: WrapMethodType, method: MethodType):
        self.queries.append(MethodBuildInfo(wrap, method))

    def register_mutation(self, wrap: WrapMethodType, method: MethodType):
        self.mutations.append(MethodBuildInfo(wrap, method))

    def register_subscription(self, wrap: WrapMethodType, method: MethodType):
        self.subscriptions.append(MethodBuildInfo(wrap, method))
