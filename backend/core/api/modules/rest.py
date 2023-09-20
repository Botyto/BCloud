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

from ...miniapp.miniapp import MiniappContext, MiniappModule, Miniapp
from ...typeinfo import MethodInfo, TypeInfo


class RestVerb(Enum):
    GET = "GET"
    POST = "POST"


@dataclass
class RestMethodInfo:
    verb: RestVerb
    partial_urlspec: PartialURLSpec


class RestApiHandler(ApiHandlerMixin, HttpApiHandler):
    pass


def get(pattern: str|Pattern, kwargs: Dict[str, Any]|None = None, name: str|None = None):
    def decorator(fn):
        rest_info = RestMethodInfo(RestVerb.GET, PartialURLSpec(pattern, kwargs, name))
        setattr(fn, "__rest__", rest_info)
        return fn
    return decorator

def post(pattern: str|Pattern, kwargs: Dict[str, Any]|None = None, name: str|None = None):
    def decorator(fn):
        rest_info = RestMethodInfo(RestVerb.POST, PartialURLSpec(pattern, kwargs, name))
        setattr(fn, "__rest__", rest_info)
        return fn
    return decorator


class RestMiniappModule(MiniappModule, RestApiHandler):
    context: ApiContext

    def __init__(self, miniapp: Miniapp, context: ApiContext):
        super().__init__(miniapp, context)

    @classmethod
    def start(cls, miniapp: Miniapp, context: MiniappContext):
        super().start(miniapp, context)
        pattern_to_methods: Dict[str|Pattern, List[MethodType]] = {}
        for method in cls._all_own_methods():
            info = getattr(method, "__rest__", None)
            if not isinstance(info, RestMethodInfo):
                continue
            pattern = info.partial_urlspec.pattern
            if pattern not in pattern_to_methods:
                pattern_to_methods[pattern] = []
            pattern_to_methods[pattern].append(method)
        for pattern, methods in pattern_to_methods.items():
            info = getattr(methods[0], "__rest__", None)
            assert isinstance(info, RestMethodInfo)
            cls.__register_handler(miniapp, context, methods, info)

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
            def wrapped_handler(self: RestApiHandler):
                args = get_query_args(self)
                with cls(miniapp, self.api_context) as obj:  # type: ignore
                    result = method(obj, *args)
                    if isinstance(result, ApiResponse):
                        result.assign(self)
            return wrapped_handler
        else:
            def wrapped_handler(self: RestApiHandler):
                args = get_query_args(self)
                obj = cls(miniapp, self.api_context)
                result = method(obj, *args)
                if isinstance(result, ApiResponse):
                    result.assign(self)
            return wrapped_handler

    @classmethod
    def __generate_handler(cls, miniapp: Miniapp, methods: List[MethodType], info: RestMethodInfo):
        attrs = {}
        for method in methods:
            wrapped_handler = cls.__generate_handler_method(miniapp, method)
            wrapped_handler.__name__ = info.verb.value.lower()
            assert method.__name__ not in attrs, "Duplicate verbs for the same URL"
            attrs[method.__name__] = wrapped_handler
        class_name = methods[0].__name__.capitalize() + "Handler"
        return type(class_name, (RestApiHandler,), attrs)
    
    @classmethod
    def __register_handler(cls, miniapp: Miniapp, context: MiniappContext, methods: List[MethodType], info: RestMethodInfo):
        handler_class = cls.__generate_handler(miniapp, methods, info)
        context.urlspecs.append(URLSpec(
            pattern=info.partial_urlspec.pattern,
            handler=handler_class,
            kwargs=info.partial_urlspec.kwargs,
            name=info.partial_urlspec.name,
        ))
