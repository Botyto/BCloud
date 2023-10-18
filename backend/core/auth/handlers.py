from datetime import datetime, timedelta, timezone
import logging
import jwt as pyjwt
from sqlalchemy.orm import Session
from tornado.httputil import HTTPServerRequest
from uuid import UUID

from .context import AuthContext
from .data import Login

from ..http.context import ServerContext

logger = logging.getLogger(__name__)


class AuthError(ValueError):
    def __init__(self, msg: str|None = None, *args):
        if msg is None:
            msg = "Invalid credentials"
        super().__init__(msg, *args)


class AuthHandlerMixin:
    request: HTTPServerRequest
    session: Session
    context: ServerContext
    user_id: UUID|None = None
    login_id: UUID|None = None

    @property
    def jwt_secret(self):
        return "test"

    @property
    def sensitive_authentication_errors(self):
        return self.context.env.debug

    @property
    def login_validity(self):
        return timedelta(days=30)

    def _get_login_jwt(self) -> str|None:
        token: str|None = self.request.headers.get("Authorization", self.request.headers.get("authorization", None))
        if token is None:
            cookie = self.request.cookies.get("Authorization", self.request.cookies.get("authorization", None))
            if cookie is not None:
                token = cookie.value
        if token is not None and token.startswith("Bearer "):
            token = token[len("Bearer "):]
        if isinstance(token, str) and token.lower() == "null":
            return
        return token
    
    def get_current_user(self):
        if self.user_id is None:
            jwt = self._get_login_jwt()
            if not jwt:
                return None
            data = pyjwt.decode(jwt, self.jwt_secret, algorithms=["HS256"])
            return self.authenticate(data)
        return self.user_id
        
    def encode_jwt(self, data: dict) -> str:
        return pyjwt.encode(data, self.jwt_secret, algorithm="HS256")

    def authenticate(self, data: dict):
        if self.user_id is not None:
            logger.warning("User already authenticated")
        login_id = UUID(data["sub"])
        login = self.session.get(Login, login_id)
        if login is None:
            if self.sensitive_authentication_errors:
                raise AuthError("Login not found")
            raise AuthError()
        if not login.enabled:
            if self.sensitive_authentication_errors:
                raise AuthError("Login disabled")
            raise AuthError()
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        if login.expire_at_utc.replace(tzinfo=timezone.utc) < now:
            if self.sensitive_authentication_errors:
                raise AuthError("Login expired")
            raise AuthError()
        # TODO ensure login is trustworthy
        self.login_id = login_id
        self.user_id = login.user_id
        login.last_used_utc = now
        login.expire_at_utc = now + self.login_validity
        return self.user_id
    
    @property
    def auth_context(self):
        self.get_current_user()
        return AuthContext(self.context, self)
