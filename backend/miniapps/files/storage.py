from uuid import UUID

from .data import FileMetadata, FileStorage
from .tools.storage import StorageManager

from core.api.modules.gql import GqlMiniappModule, query, mutation
from core.api.pages import PagesInput, PagesResult
from core.auth.handlers import AuthError
from core.graphql.result import SuccessResult


class StorageModule(GqlMiniappModule):
    _manager: StorageManager|None = None

    @property
    def manager(self):
        if self._manager is None:
            if self.user_id is None:
                raise AuthError()
            self._manager = StorageManager(self.user_id, self.session)
        return self._manager

    @query()
    def list(self, pages: PagesInput) -> PagesResult[FileStorage]:
        return self.manager.list(pages)
    
    @query()
    def metadata(self, id: UUID) -> FileStorage:
        return self.manager.get(id)
    
    @query()
    def root(self, id: UUID) -> FileMetadata:
        return self.manager.root(id)
    
    @mutation()
    def create(self, name: str) -> FileStorage:
        storage = self.manager.create(name)
        self.log_activity("storage.create", {"id": str(storage.id), "name": name})
        return storage

    @mutation()
    def delete(self, id: UUID) -> SuccessResult:
        success, name = self.manager.delete(id)
        if success:
            self.log_activity("storage.delete", {"id": str(id), "name": name})
        return SuccessResult(success)
    
    @mutation()
    def rename(self, id: UUID, name: str) -> FileStorage:
        storage, previous = self.manager.rename(id, name)
        self.log_activity("storage.rename", {"id": str(id), "new": name, "old": previous})
        return storage
