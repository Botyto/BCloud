from dataclasses import dataclass
from enum import Enum
import functools
from types import MethodType
from typing import cast

from ..gql import GraphQLModule, GraphQLSubscriptionModule

from ...auth.data import Activity
from ...data.sql.columns import utcnow_tz
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
        self.handler.get_current_user()
        return self.handler.user_id
    
    @property
    def login_id(self):
        self.handler.get_current_user()
        return self.handler.login_id
    
    def log_activity(self, type: str, payload: dict|None = None):
        self.handler.get_current_user()
        activity = Activity(
            created_at_utc=utcnow_tz(),
            issuer=self.miniapp.id,
            user_id=self.user_id,
            type=type,
            payload=payload,
        )
        self.session.add(activity)
        return activity
    
    @classmethod
    def __all_own_methods(cls):
        all_attributes = [getattr(cls, m) for m in dir(cls)]
        return [m for m in all_attributes if callable(m)]

    @classmethod
    def start(cls, miniapp: Miniapp, context: MiniappContext):
        super().start(miniapp, context)
        for method in cls.__all_own_methods():
            if not hasattr(method, "__gql__"):
                continue
            info = cast(GqlMethodInternals, getattr(method, "__gql__", None))
            cls.__register_method(miniapp, context, method, info)

    @classmethod
    def __make_wrapper(cls, miniapp: Miniapp):
        def wrapper(minfo: GqlMethodInfo):
            fn = minfo.wrap(miniapp)
            @functools.wraps(fn)
            def commit_wrapper(root, *args, **kwargs):
                result = fn(root, *args, **kwargs)
                if root._session is not None:
                    root._session.commit()
                return result
            return commit_wrapper
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
