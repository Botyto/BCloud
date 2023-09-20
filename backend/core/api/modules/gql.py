
from dataclasses import dataclass
from enum import Enum
from types import MethodType


from .rest import RestMiniappModule

from ...graphql.context import GraphQLContext
from ...miniapp.miniapp import MiniappContext, Miniapp


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
    context: GraphQLContext

    def __init__(self, root, context: GraphQLContext):
        self.context = context

    @classmethod
    def start(cls, miniapp: Miniapp, context: MiniappContext):
        super().start(miniapp, context)
        for method in cls._all_own_methods():
            info = getattr(method, "__gql__", None)
            if not isinstance(info, GqlMethodInfo):
                continue
            cls.__register_method(miniapp, context, method, info)

    @classmethod
    def __register_method(cls, miniapp: Miniapp, context: MiniappContext, method: MethodType, info: GqlMethodInfo):
        match info.method:
            case GqlMethod.QUERY:
                context.graphql_methods.queries.append(method)
            case GqlMethod.MUTATION:
                context.graphql_methods.mutations.append(method)
            case GqlMethod.SUBSCRIPTION:
                context.graphql_methods.subscriptions.append(method)
            case _:
                raise ValueError(f"Unknown GraphQL method {info.method}")
