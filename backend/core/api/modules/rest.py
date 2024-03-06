from dataclasses import dataclass
from enum import Enum
from functools import partial
from re import Pattern
from tornado.routing import URLSpec
from types import MethodType
from typing import Any, Dict, List

from .api import PartialURLSpec
from ..context import ApiContext
from ..handlers import HttpApiHandler, ApiHandlerMixin, ApiResponse

from ...auth.data import Activity
from ...data.sql.columns import utcnow_tz
from ...http.handlers import SessionHandlerMixin
from ...miniapp.miniapp import MiniappContext, MiniappModule, Miniapp
from ...typeinfo import MethodInfo, TypeInfo


class RestVerb(Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"


@dataclass
class RestMethodInternals:
    verb: RestVerb
    partial_urlspec: PartialURLSpec


class RestApiHandler(ApiHandlerMixin, HttpApiHandler):
    pass


def get(pattern: str|Pattern, kwargs: Dict[str, Any]|None = None, name: str|None = None):
    def decorator(fn):
        internals = RestMethodInternals(RestVerb.GET, PartialURLSpec(pattern, kwargs, name))
        setattr(fn, "__rest__", internals)
        return fn
    return decorator

def post(pattern: str|Pattern, kwargs: Dict[str, Any]|None = None, name: str|None = None):
    def decorator(fn):
        internals = RestMethodInternals(RestVerb.POST, PartialURLSpec(pattern, kwargs, name))
        setattr(fn, "__rest__", internals)
        return fn
    return decorator

def delete(pattern: str|Pattern, kwargs: Dict[str, Any]|None = None, name: str|None = None):
    def decorator(fn):
        internals = RestMethodInternals(RestVerb.DELETE, PartialURLSpec(pattern, kwargs, name))
        setattr(fn, "__rest__", internals)
        return fn
    return decorator

def put(pattern: str|Pattern, kwargs: Dict[str, Any]|None = None, name: str|None = None):
    def decorator(fn):
        internals = RestMethodInternals(RestVerb.PUT, PartialURLSpec(pattern, kwargs, name))
        setattr(fn, "__rest__", internals)
        return fn
    return decorator


class RestMiniappModule(MiniappModule, RestApiHandler):
    _context: ApiContext|None = None

    def __init__(self, miniapp: Miniapp, application, request, **kwargs):
        super(MiniappModule, self).__init__(application, request, **kwargs)
        super().__init__(miniapp, self.api_context)

    @SessionHandlerMixin.context.getter
    def context(self):
        return self._context or SessionHandlerMixin.context.fget(self)

    @context.setter
    def context(self, value: ApiContext):
        self._context = value

    def log_activity(self, type: str, payload: dict|None = None):
        self.get_current_user()
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
    def start(cls, miniapp: Miniapp, context: MiniappContext):
        super().start(miniapp, context)
        pattern_to_methods: Dict[str|Pattern, List[MethodType]] = {}
        for method in cls._all_own_methods():
            info = getattr(method, "__rest__", None)
            if not isinstance(info, RestMethodInternals):
                continue
            pattern = info.partial_urlspec.pattern
            if pattern not in pattern_to_methods:
                pattern_to_methods[pattern] = []
            pattern_to_methods[pattern].append(method)
        for pattern, methods in pattern_to_methods.items():
            info = getattr(methods[0], "__rest__", None)
            assert isinstance(info, RestMethodInternals)
            cls.__register_handler(miniapp, context, methods)

    @classmethod
    def _all_own_methods(cls):
        all_attributes = [getattr(cls, m) for m in dir(cls)]
        return [m for m in all_attributes if callable(m)]
    
    @staticmethod
    def __get_query_args(list_args: List[bool], param_names: List[str], defaults: Dict[str, Any], handler: RestApiHandler):
        result = []
        for i, name in enumerate(param_names):
            if list_args[i]:
                arg_value = handler.get_query_arguments(name)
            else:
                arg_value = handler.get_query_argument(name, defaults.get(name))
            result.append(arg_value)
        return result

    @classmethod
    def __generate_handler_method(cls, miniapp: Miniapp, method: MethodType):
        method_info = MethodInfo(method)
        get_query_args = partial(
            cls.__get_query_args,
            [TypeInfo(type, True).is_list for _, type in method_info.param_types.items()],
            method_info.param_names,
            method_info.param_defaults,
        )
        if method_info.is_async:
            pass
        if method_info.is_context_manager:
            def wrapped_handler(self: RestApiHandler, *args):
                if not args:
                    args = get_query_args(self)
                with self:  # type: ignore
                    result = method(self, *args)
                    if isinstance(result, ApiResponse):
                        result.assign(self)
            return wrapped_handler
        else:
            def wrapped_handler(self: RestApiHandler, *args):
                if not args:
                    args = get_query_args(self)
                result = method(self, *args)
                if isinstance(result, ApiResponse):
                    result.assign(self)
            return wrapped_handler

    @classmethod
    def __generate_handler(cls, miniapp: Miniapp, methods: List[MethodType]):
        attrs = {}
        for method in methods:
            wrapped_handler = cls.__generate_handler_method(miniapp, method)
            info: RestMethodInternals = getattr(method, "__rest__")
            verb = info.verb.value.lower()
            assert verb not in attrs, "Duplicate verbs for the same URL"
            attrs[verb] = wrapped_handler
        class_name = methods[0].__name__.capitalize() + "Handler"
        def ctor(self, application, request):
            super(cls, self).__init__(miniapp, application, request)  # type: ignore
        attrs["__init__"] = ctor
        return type(class_name, (cls,), attrs)
    
    @classmethod
    def __register_handler(cls, miniapp: Miniapp, context: MiniappContext, methods: List[MethodType]):
        first_info: RestMethodInternals = getattr(methods[0], "__rest__")
        handler_class = cls.__generate_handler(miniapp, methods)
        context.urlspecs.append(URLSpec(
            pattern=first_info.partial_urlspec.pattern,
            handler=handler_class,
            kwargs=first_info.partial_urlspec.kwargs,
            name=first_info.partial_urlspec.name,
        ))
