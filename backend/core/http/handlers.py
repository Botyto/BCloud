import logging
from sqlalchemy.exc import PendingRollbackError
import traceback
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
from typing import Any

from .context import ServerContext

from ..data.sql.database import Session

logger = logging.getLogger(__name__)


class SessionHandlerMixin(RequestHandler):
    _session: Session|None = None

    def _make_session_info(self):
        return {"handler": self}

    @property
    def context(self) -> ServerContext:
        return self.application.settings["server_context"]

    @property
    def session(self):
        if self._session is None:
            info = self._make_session_info()
            database = self.context.database
            self._session = database.make_session(info)
        return self._session

    def send_error(self, status_code: int = 500, **kwargs: Any):
        if self._session is not None:
            self._session.rollback()
            self._session.close()
            del self._session
        return super().send_error(status_code, **kwargs)

    def on_finish(self):
        if self._session is not None:
            try:
                self._session.commit()
            except PendingRollbackError as e:
                logger.exception(e)
            self._session.close()


class ApiHandler(SessionHandlerMixin, RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "authorization, content-type")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, PATCH, DELETE, OPTIONS')
        return super().set_default_headers()

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        result = {"code": status_code, "error": self._reason}
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            result["traceback"] = traceback.format_exception(*kwargs["exc_info"])
        self.write(result)
        self.finish()


class WebSocketApiHandler(SessionHandlerMixin, WebSocketHandler):
    def check_origin(self, origin):
        # TODO check documentation of super function
        return True
