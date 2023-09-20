from dataclasses import dataclass
from enum import Enum
from types import MethodType

from .rest import RestMiniappModule

from ...miniapp.miniapp import MiniappContext


class GqlMethod(Enum):
    QUERY = "QUERY"
    MUTATION = "MUTATION"
    SUBSCRIPTION = "SUBSCRIPTION"


@dataclass
class GqlMethodInfo:
    method: GqlMethod

def query():
    def decorator(fn):
        fn.__gql__ = GqlMethodInfo(GqlMethod.QUERY)
        return fn
    return decorator

def mutation():
    def decorator(fn):
        fn.__gql__ = GqlMethodInfo(GqlMethod.MUTATION)
        return fn
    return decorator

def subscription():
    def decorator(fn):
        fn.__gql__ = GqlMethodInfo(GqlMethod.SUBSCRIPTION)
        return fn
    return decorator


class GqlMiniappModule(RestMiniappModule):
    def start(self, context: MiniappContext):
        super().start(context)
        for method in self._all_own_methods():
            info = getattr(method, "__gql__", None)
            if not isinstance(info, GqlMethodInfo):
                continue
            self.__register_method(context, method, info)

    def __register_method(self, context: MiniappContext, method: MethodType, info: GqlMethodInfo):
        match info.method:
            case GqlMethod.QUERY:
                context.graphql_methods.queries.append(method)
            case GqlMethod.MUTATION:
                context.graphql_methods.mutations.append(method)
            case GqlMethod.SUBSCRIPTION:
                context.graphql_methods.subscriptions.append(method)
            case _:
                raise ValueError(f"Unknown GraphQL method {info.method}")
