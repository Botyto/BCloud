from dataclasses import dataclass
from functools import partial
from re import Pattern
from tornado.httputil import HTTPServerRequest
from tornado.routing import URLSpec
from tornado.web import Application, RequestHandler
from typing import Any, Dict

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


class ApiMiniappModule(MiniappModule, RequestHandler):
    __urlspec__: PartialURLSpec

    def __init__(self, miniapp: Miniapp):
        super().__init__(miniapp)

    def start(self, context: MiniappContext):
        super().start(context)
        self_class = self.__class__
        self_miniapp = self.miniapp
        def handler_init(self, application: Application, request: HTTPServerRequest|None = None, **kwargs):
            super(ApiMiniappModule, self).__init__(self_miniapp)
            super(MiniappModule, self).__init__(application, request, **kwargs)
        handler_class = type(self.__class__.__name__ + "Handler", (self.__class__,), {
            "__init__": handler_init,
        })
        context.urlspecs.append(URLSpec(
            pattern=self.__urlspec__.pattern,
            handler=handler_class,
            kwargs=self.__urlspec__.kwargs,
            name=self.__urlspec__.name,
        ))
