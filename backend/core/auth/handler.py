from datetime import datetime, timedelta, timezone
import logging
import jwt
from sqlalchemy.orm import Session
from tornado.httputil import HTTPServerRequest
from uuid import UUID

from .data import UserSession

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
    _user_id: UUID|None = None
    _login_id: str|None = None

    @property
    def jwt_secret(self):
        return "test"

    @property
    def sensitive_authentication_errors(self):
        return self.context.env.debug

    @property
    def session_validity(self):
        return timedelta(days=30)

    def _get_session_data(self) -> dict|None:
        header = self.request.headers.get("Authorization", None)
        if header is None:
            return None
        return jwt.decode(header, self.jwt_secret, algorithms=["HS256"])

    def get_current_user(self):
        if self._user_id is None:
            data = self._get_session_data()
            if data is None:
                return None
            return self.authenticate(data)

    def authenticate(self, data: dict):
        if self._user_id is not None:
            logger.warning("User already authenticated")
        session_id = data["sub"]
        session_obj = self.session.get(UserSession, session_id)
        if session_obj is None:
            if self.sensitive_authentication_errors:
                raise AuthError("Session not found")
            raise AuthError()
        if not session_obj.enabled:
            if self.sensitive_authentication_errors:
                raise AuthError("Session disabled")
            raise AuthError()
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        if session_obj.expire_at_utc.replace(tzinfo=timezone.utc) < now:
            if self.sensitive_authentication_errors:
                raise AuthError("Session expired")
            raise AuthError()
        # TODO ensure session is trustworthy
        self._login_id = session_id
        self._user_id = session_obj.user_id
        session_obj.last_used_utc = now
        session_obj.expire_at_utc = now + self.session_validity
        return self._user_id
