from ..miniapp.context import MiniappContext
from ..miniapp.engine import Manager as MiniappsManager


class AppContext(MiniappContext):
    miniapps: MiniappsManager

    def __init__(self,
        base: MiniappContext,
        miniapps: MiniappsManager,
    ):
        self._extend(base)
        self.miniapps = miniapps
