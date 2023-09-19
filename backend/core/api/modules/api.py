from dataclasses import dataclass
from functools import partial
from re import Pattern
from tornado.routing import URLSpec
from typing import Any, Dict

from ...miniapp.miniapp import MiniappContext, MiniappModule


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


class ApiMiniappModule(MiniappModule):
    __urlspec__: PartialURLSpec

    def start(self, context: MiniappContext):
        super().start(context)
        context.urlspecs.append(URLSpec(
            pattern=self.__urlspec__.pattern,
            handler=partial(self.__class__, self.miniapp),
            kwargs=self.__urlspec__.kwargs,
            name=self.__urlspec__.name,
        ))
