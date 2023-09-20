from dataclasses import dataclass
from re import Pattern
from tornado.httputil import HTTPServerRequest
from tornado.routing import URLSpec
from tornado.web import Application
from typing import Any, Dict

from ..handlers import ApiHandler
from ...miniapp.miniapp import MiniappContext, MiniappModule, Miniapp


@dataclass
class PartialURLSpec:
    pattern: str|Pattern
    kwargs: Dict[str, Any]|None
    name: str|None

def urlspec(pattern: str|Pattern, kwargs: Dict[str, Any]|None = None, name: str|None = None):
    def decorator(cls):
        partial_urlspec = PartialURLSpec(pattern, kwargs, name)
        setattr(cls, "__urlspec__", partial_urlspec)
        return cls
    return decorator


class ApiMiniappModule(MiniappModule, ApiHandler):
    __urlspec__: PartialURLSpec

    @ApiHandler.context.setter
    def context(self, _):
        pass

    @classmethod
    def start(cls, miniapp: Miniapp, context: MiniappContext):
        super().start(miniapp, context)
        assert cls.__urlspec__ is not None, "ApiMiniappModule must be decorated with @urlspec"
        def handler_init(self, application: Application, request: HTTPServerRequest|None = None, **kwargs):
            super(ApiMiniappModule, self).__init__(miniapp, context)
            super(MiniappModule, self).__init__(application, request, **kwargs)  # type: ignore
        handler_class = type(cls.__name__ + "Handler", (cls,), {
            "__init__": handler_init,
        })
        context.urlspecs.append(URLSpec(
            pattern=cls.__urlspec__.pattern,
            handler=handler_class,
            kwargs=cls.__urlspec__.kwargs,
            name=cls.__urlspec__.name,
        ))
