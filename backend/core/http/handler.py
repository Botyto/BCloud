import traceback
from tornado.web import RequestHandler
from typing import Any


class BaseHandler(RequestHandler):
    pass


class ApiHandler(BaseHandler):
    def write_error(self, status_code: int, **kwargs: Any) -> None:
        result = {
            "code": status_code,
            "error": self._reason,
        }
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            result["traceback"] = traceback.format_exception(*kwargs["exc_info"])
        self.write(result)
        self.finish()
