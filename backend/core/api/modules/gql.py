from dataclasses import dataclass
from enum import Enum
from types import MethodType
from typing import cast

from ..gql import GraphQLModule, GraphQLSubscriptionModule

from ...graphql.context import GraphQLContext
from ...graphql.typeinfo import GqlMethodInfo
from ...miniapp.miniapp import MiniappContext, MiniappModule, Miniapp


class GqlMethod(Enum):
    QUERY = "QUERY"
    MUTATION = "MUTATION"
    SUBSCRIPTION = "SUBSCRIPTION"


@dataclass
class GqlMethodInternals:
    method: GqlMethod

def query():
    def decorator(fn):
        setattr(fn, "__gql__", GqlMethodInternals(GqlMethod.QUERY))
        return fn
    return decorator

def mutation():
    def decorator(fn):
        setattr(fn, "__gql__", GqlMethodInternals(GqlMethod.MUTATION))
        return fn
    return decorator

def subscription():
    def decorator(fn):
        setattr(fn, "__gql__", GqlMethodInternals(GqlMethod.SUBSCRIPTION))
        return fn
    return decorator


class GqlMiniappModule(MiniappModule):
    handler: GraphQLModule|GraphQLSubscriptionModule
    context: GraphQLContext

    def __init__(self, handler: GraphQLModule|GraphQLSubscriptionModule, context: GraphQLContext, miniapp: Miniapp):
        super().__init__(miniapp, context)
        self.handler = handler

    @property
    def session(self):
        return self.handler.session
    
    @property
    def user_id(self):
        return self.handler.user_id
    
    @property
    def login_id(self):
        return self.handler.login_id
    
    @classmethod
    def _all_own_methods(cls):
        all_attributes = [getattr(cls, m) for m in dir(cls)]
        return [m for m in all_attributes if callable(m)]

    @classmethod
    def start(cls, miniapp: Miniapp, context: MiniappContext):
        super().start(miniapp, context)
        for method in cls._all_own_methods():
            if not hasattr(method, "__gql__"):
                continue
            info = cast(GqlMethodInternals, getattr(method, "__gql__", None))
            cls.__register_method(miniapp, context, method, info)

    @classmethod
    def __make_wrapper(cls, miniapp: Miniapp):
        def wrapper(minfo: GqlMethodInfo):
            return minfo.wrap(miniapp)
        return wrapper

    @classmethod
    def __register_method(cls, miniapp: Miniapp, context: MiniappContext, method: MethodType, info: GqlMethodInternals):
        wrapper = cls.__make_wrapper(miniapp)
        match info.method:
            case GqlMethod.QUERY:
                context.graphql_methods.register_query(wrapper, method)
            case GqlMethod.MUTATION:
                context.graphql_methods.register_mutation(wrapper, method)
            case GqlMethod.SUBSCRIPTION:
                context.graphql_methods.register_subscription(wrapper, method)
            case _:
                raise ValueError(f"Unknown GraphQL method {info.method}")
