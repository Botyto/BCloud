from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session
from uuid import UUID, uuid4

from ..data import FileMetadata, FileStorage, DIRECTORY_MIME

from core.api.pages import PagesInput
from core.data.sql.columns import ensure_str_fit


class StorageManager:
    SERVICE_PREFIX = "__app_"

    user_id: UUID
    session: Session

    def __init__(self, user_id: UUID, session: Session):
        self.user_id = user_id
        self.session = session

    def list(self, pages: PagesInput):
        statement = select(FileStorage) \
            .where(FileStorage.user_id == self.user_id)
        def discard_service(storage: FileStorage):
            return not storage.name.startswith(self.SERVICE_PREFIX)
        return pages.of(self.session, statement, discard_service)
    
    def get(self, id: UUID):
        statement = select(FileStorage) \
            .where(FileStorage.user_id == self.user_id) \
            .where(FileStorage.id == id)
        return self.session.scalars(statement).one()
    
    def root(self, id: UUID):
        return self.get(id).root_dir
    
    def create(self, name: str, *, service: bool = False):
        if not service and name.startswith(self.SERVICE_PREFIX):
            raise ValueError(f"Storage name cannot start with {self.SERVICE_PREFIX}")
        ensure_str_fit("name", name, FileStorage.name)
        root = FileMetadata(id=uuid4(), name="root", mime_type=DIRECTORY_MIME)
        storage = FileStorage(id=uuid4(), name=name, user_id=self.user_id)
        storage.root_dir = root
        root.storage = storage
        self.session.add(storage)
        return storage
    
    def delete(self, id: UUID):
        statement = delete(FileStorage) \
            .where(FileStorage.user_id == self.user_id) \
            .where(FileStorage.id == id) \
            .returning(FileStorage.name)
        result = self.session.execute(statement)
        name = result.scalar_one()
        return True, name
    
    def rename(self, id: UUID, name: str):
        ensure_str_fit("name", name, FileStorage.name)
        # OPTIMIZE: make both the old-value-getter and the update in one statement
        get_statement = select(FileStorage) \
            .where(FileStorage.user_id == self.user_id) \
            .where(FileStorage.id == id)
        storage = self.session.scalars(get_statement).one()
        old_name = storage.name
        storage.name = name
        return storage, old_name
