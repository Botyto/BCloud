import time

from ..asyncjob.context import AsyncJobContext
from ..asyncjob.engine import AsyncJobs


class MiniappContext(AsyncJobContext):
    miniapp_init_time: float
    asyncjobs: AsyncJobs

    def __init__(self,
        base: AsyncJobContext,
        asyncjobs: AsyncJobs,
    ):
        self._extend(base)
        self.miniapp_init_time = time.time()
        self.asyncjobs = asyncjobs
