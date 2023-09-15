from typing import cast

from ..app.main import AppContext


class ServerContext(AppContext):
    def __init__(self, base: AppContext):
        self._extend(base)

    @property
    def port(self):
        return cast(int, self.env.get("PORT", 8080))
