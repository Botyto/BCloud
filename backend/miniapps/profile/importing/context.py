from uuid import UUID

from core.asyncjob.context import AsyncJobRuntimeContext


class ImportingContext(AsyncJobRuntimeContext):
    user_id: UUID

    def __init__(self, base: AsyncJobRuntimeContext, user_id: UUID):
        self._extend(base)
        self.user_id = user_id
