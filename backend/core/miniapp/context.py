from ..asyncjob.context import AsyncJobContext
from ..asyncjob.engine import AsyncJobs
from ..data.blobs.base import Blobs


class MiniappContext(AsyncJobContext):
    files: Blobs
    asyncjobs: AsyncJobs

    def __init__(self,
        base: AsyncJobContext,
        files: Blobs,
        asyncjobs: AsyncJobs,
    ):
        self._extend(base)
        self.files = files
        self.asyncjobs = asyncjobs
