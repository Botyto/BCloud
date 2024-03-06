from typing import Dict, List

from .context import ApiContext

from ..auth.handlers import AuthHandlerMixin
from ..http.handlers import HttpApiHandler


class ApiHandlerMixin(AuthHandlerMixin):
    @property
    def api_context(self):
        return ApiContext(self.auth_context)


class ApiHandler(ApiHandlerMixin, HttpApiHandler):
    pass


class ApiResponse:
    headers: Dict[str, List[str]]
    status: int|None
    content: bytes|str|None

    def __init__(self, *, status: int|None = None, content: bytes|str|None = None, **headers: List[str]|str):
        # parse headers
        parsed_headers: Dict[str, List[str]] = {}
        for name, values in headers.items():
            if isinstance(values, str):
                values = [values]
            parsed_headers[name] = values
        # init members
        self.headers = parsed_headers
        self.status = status
        self.content = content

    def add_header(self, name: str, value: str):
        values_list = self.headers.get(name)
        if not values_list:
            values_list = []
            self.headers[name] = values_list
        values_list.append(value)

    def set_header(self, name: str, value: str):
        self.headers[name] = [value]

    def set_status(self, status: int):
        self.status = status

    def write(self, content: bytes|str):
        self.content = content

    def assign(self, handler: HttpApiHandler):
        for name, values in self.headers.items():
            for value in values:
                handler.add_header(name, value)
        if self.status is not None:
            handler.set_status(self.status)
        if self.content is not None:
            handler.write(self.content)
