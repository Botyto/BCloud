from typing import Callable, Dict

from .context import AsyncJobRuntimeContext


HandlerType = Callable[[AsyncJobRuntimeContext], None]


class IssuerMap:
    issuer: str
    handlers: Dict[str, HandlerType]

    def __init__(self, app_id: str):
        self.issuer = app_id
        self.handlers = {}

    def add(self, type: str, handler: HandlerType):
        assert type not in self.handlers, f"Job type {self.issuer}.{type} already registered"
        self.handlers[type] = handler

    def resolve(self, type: str) -> HandlerType|None:
        return self.handlers.get(type)


class JobHandlers:
    by_issuer: Dict[str, IssuerMap]

    def __init__(self):
        self.by_issuer = {}

    def add(self, issuer: str, type: str, handler: HandlerType):
        app_handler = self.by_issuer.get(issuer)
        if app_handler is None:
            app_handler = IssuerMap(issuer)
            self.by_issuer[issuer] = app_handler
        app_handler.add(type, handler)

    def resolve(self, issuer: str, type: str) -> HandlerType|None:
        app_handler = self.by_issuer.get(issuer)
        if app_handler is None:
            return None
        return app_handler.handlers.get(type)
