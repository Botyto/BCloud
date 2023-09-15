import logging
from sqlalchemy.exc import PendingRollbackError
import traceback
from tornado.web import RequestHandler
from typing import Any

from .context import ServerContext

from ..data.sql.database import Session

logger = logging.getLogger(__name__)


class SessionHandler(RequestHandler):
    _session: Session

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


class ApiHandler(SessionHandler):
    def write_error(self, status_code: int, **kwargs: Any) -> None:
        result = {"code": status_code, "error": self._reason}
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            result["traceback"] = traceback.format_exception(*kwargs["exc_info"])
        self.write(result)
        self.finish()
