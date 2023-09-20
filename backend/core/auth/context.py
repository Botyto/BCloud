from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .handlers import AuthHandlerMixin

from ..http.context import ServerContext


class AuthContext(ServerContext):
    handler: "AuthHandlerMixin"

    def __init__(self, base: ServerContext, handler: "AuthHandlerMixin"):
        self._extend(base)
        self.handler = handler

    @property
    def user_id(self):
        return self.handler.user_id
    
    @property
    def login_id(self):
        return self.handler.login_id
