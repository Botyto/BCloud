from sqlalchemy import delete, select, update
from uuid import UUID


from core.api.modules.gql import GqlMiniappModule, query, mutation
from core.api.pages import PagesInput, PagesResult
from core.graphql.result import SuccessResult
from core.data.sql.columns import ensure_str_fit

from .data import FileMetadata, FileStorage, DIRECTORY_MIME


class StorageModule(GqlMiniappModule):
    SERVICE_PREFIX = "__app_"

    @query()
    def list(self, pages: PagesInput) -> PagesResult[FileStorage]:
        statement = select(FileStorage) \
            .where(FileStorage.owner_id == self.user_id)
        def discard_service(storage: FileStorage):
            return not storage.name.startswith(self.SERVICE_PREFIX)
        return pages.of(self.session, statement, discard_service)
    
    @query()
    def metadata(self, id: UUID) -> FileStorage:
        statement = select(FileStorage) \
            .where(FileStorage.owner_id == self.user_id) \
            .where(FileStorage.id == id)
        return self.session.scalars(statement).one()
    
    @query()
    def root(self, id: UUID) -> FileMetadata:
        return self.metadata(id).root_dir
    
    def _create(self, name: str) -> FileStorage:
        ensure_str_fit("name", name, FileStorage.name)
        root = FileMetadata(name="root", mime_type=DIRECTORY_MIME, size=0)
        storage = FileStorage(name=name, owner_id=self.user_id)
        storage.root_dir = root
        root.storage = storage
        self.session.add(storage)
        return storage

    @mutation()
    def create(self, name: str) -> FileStorage:
        if name.startswith(self.SERVICE_PREFIX):
            raise ValueError(f"Storage name cannot start with {self.SERVICE_PREFIX}")
        return self._create(name)

    @mutation()
    def delete(self, id: UUID) -> SuccessResult:
        statement = delete(FileStorage) \
            .where(FileStorage.owner_id == self.user_id) \
            .where(FileStorage.id == id)
        result = self.session.execute(statement)
        return SuccessResult(result.rowcount != 0)
    
    @mutation()
    def rename(self, id: UUID, name: str) -> FileStorage:
        ensure_str_fit("name", name, FileStorage.name)
        statement = update(FileStorage) \
            .where(FileStorage.owner_id == self.user_id) \
            .where(FileStorage.id == id) \
            .values(name=name)
        result = self.session.scalars(statement).one()
        return result
