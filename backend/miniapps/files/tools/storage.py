from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload
from uuid import UUID, uuid4

from ..data import FileMetadata, FileStorage, DIRECTORY_MIME

from core.api.pages import PagesInput
from core.auth.handlers import AuthError
from core.data.sql.columns import ensure_str_fit, utcnow_tz


class StorageManager:
    SERVICE_PREFIX = "__app_"

    user_id: UUID|None
    session: Session
    service: bool = False

    def __init__(self, user_id: UUID|None, session: Session, service: bool = False):
        self.user_id = user_id
        self.session = session
        self.service = service

    @classmethod
    def for_service(cls, user_id: UUID|None, session: Session):
        return cls(user_id, session, service=True)

    def list(self, pages: PagesInput):
        statement = select(FileStorage)
        if self.user_id is not None:
            statement = statement.where(FileStorage.user_id == self.user_id)
        def discard_service(storage: FileStorage):
            return not storage.name.startswith(self.SERVICE_PREFIX)
        return pages.of(self.session, statement, discard_service)
    
    def _get_statement(self, id_or_slug: UUID|str):
        statement = select(FileStorage)
        if self.user_id is not None:
            statement = statement.where(FileStorage.user_id == self.user_id)
        if isinstance(id_or_slug, UUID):
            statement = statement.where(FileStorage.id == id_or_slug)
        else:
            statement = statement.where(FileStorage.slug == id_or_slug)
        return statement
    
    def by_name(self, name: str):
        statement = select(FileStorage)
        if self.user_id is not None:
            statement = statement.where(FileStorage.user_id == self.user_id)
        statement = statement.where(FileStorage.name == name)
        return self.session.scalars(statement).first()
    
    def get(self, id_or_slug: UUID|str):
        statement = self._get_statement(id_or_slug)
        return self.session.scalars(statement).one()
    
    def get_or_create(self, name: str):
        storage = self.by_name(name)
        if storage:
            return storage
        return self.create(name)

    def root(self, id_or_slug: UUID|str):
        statement = self._get_statement(id_or_slug) \
            .options(joinedload(FileStorage.root_dir))
        storage = self.session.scalars(statement).one()
        return storage.root_dir
    
    def create(self, name: str):
        if not self.service and name.startswith(self.SERVICE_PREFIX):
            raise ValueError(f"Storage name cannot start with {self.SERVICE_PREFIX}")
        if not name:
            raise ValueError("Storage name cannot be empty")
        if self.user_id is None:
            raise AuthError("Cannot create storages without a user")
        ensure_str_fit("name", name, FileStorage.name)
        root = FileMetadata(
            id=uuid4(),
            name="root",
            mime_type=DIRECTORY_MIME,
            ctime_utc=utcnow_tz(),
            mtime_utc=utcnow_tz(),
            atime_utc=utcnow_tz())
        storage = FileStorage(id=uuid4(), name=name, user_id=self.user_id)
        storage.root_dir = root
        root.storage = storage
        self.session.add(storage)
        return storage
    
    def delete(self, id_or_slug: UUID|str):
        statement = delete(FileStorage)
        if self.user_id is not None:
            statement = statement.where(FileStorage.user_id == self.user_id)
        statement = statement.returning(FileStorage.name)
        if isinstance(id_or_slug, UUID):
            statement = statement.where(FileStorage.id == id_or_slug)
        else:
            statement = statement.where(FileStorage.slug == id_or_slug)
        result = self.session.execute(statement)
        name = result.scalar_one()
        return True, name
    
    def rename(self, id_or_slug: UUID|str, name: str):
        if not name:
            raise ValueError("Storage name cannot be empty")
        ensure_str_fit("name", name, FileStorage.name)
        # OPTIMIZE: make both the old-value-getter and the update in one statement
        statement = select(FileStorage)
        if self.user_id is not None:
            statement = statement.where(FileStorage.user_id == self.user_id)
        if isinstance(id_or_slug, UUID):
            statement = statement.where(FileStorage.id == id_or_slug)
        else:
            statement = statement.where(FileStorage.slug == id_or_slug)
        storage = self.session.scalars(statement).one()
        old_name = storage.name
        storage.name = name
        return storage, old_name
