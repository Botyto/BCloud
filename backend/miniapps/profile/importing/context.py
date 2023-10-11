from typing import TYPE_CHECKING
from uuid import UUID

from core.asyncjob.context import AsyncJobRuntimeContext
from core.asyncjob.handlers import AsyncJobHandler


class ImportingContext(AsyncJobRuntimeContext):
    job_handler: AsyncJobHandler
    user_id: UUID

    def __init__(self, base: AsyncJobRuntimeContext, job_handler: AsyncJobHandler, user_id: UUID):
        self._extend(base)
        self.job_handler = job_handler
        self.user_id = user_id

    def temp_file_addr(self, *parts):
        return self.job_handler.temp_file_addr(*parts)
