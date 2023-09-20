import time

from ..miniapp.context import MiniappContext
from ..miniapp.engine import Manager as MiniappsManager


class AppContext(MiniappContext):
    app_init_time: float
    miniapps: MiniappsManager

    def __init__(self,
        base: MiniappContext,
        miniapps: MiniappsManager,
    ):
        self._extend(base)
        self.app_init_time = time.time()
        self.miniapps = miniapps
