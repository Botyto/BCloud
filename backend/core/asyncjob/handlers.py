from enum import Enum
from typing import Callable, Dict

from .state import State


class Action(Enum):
    RUN = "RUN"
    DELETE = "DELETE"
    CANCEL = "CANCEL"


HandlerType = Callable[[Action, State|None, int, dict], None]


class IssuerHandlers:
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
    app_handlers: Dict[str, IssuerHandlers]

    def __init__(self):
        self.app_handlers = {}

    def add(self, issuer: str, type: str, handler: HandlerType):
        app_handler = self.app_handlers.get(issuer)
        if app_handler is None:
            app_handler = IssuerHandlers(issuer)
            self.app_handlers[issuer] = app_handler
        app_handler.add(type, handler)

    def resolve(self, issuer: str, type: str) -> HandlerType|None:
        app_handler = self.app_handlers.get(issuer)
        if app_handler is None:
            return None
        return app_handler.handlers.get(type)