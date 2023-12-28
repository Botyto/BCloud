from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import ForeignKey, Enum as SqlEnum
from typing import Generator, List, Tuple, Optional
from uuid import UUID as PyUUID, uuid4

from .tools import fspath

from core.auth.access import AccessLevel
from core.auth.data import User
from core.data.sql.columns import DateTime, Integer, String, UUID
from core.data.sql.columns import Mapped, mapped_column, relationship
from core.data.sql.database import Model
from core.data.sql.slugs import SLUG_LENGTH

MIME_MAX_LENGTH = 127
DIRECTORY_MIME = "application/x-bcloud-dir"
assert len(DIRECTORY_MIME) <= MIME_MAX_LENGTH
LINK_MIME = "application/x-bcloud-link"
assert len(DIRECTORY_MIME) <= MIME_MAX_LENGTH


class FileType(Enum):
    FILE = 0
    DIRECTORY = 1
    LINK = 2


class FileMetadata(Model):
    __tablename__ = "FileMetadata"
    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(512))
    mime_type: Mapped[str|None] = mapped_column(String(MIME_MAX_LENGTH), default=None, nullable=True)
    size: Mapped[int|None] = mapped_column(Integer, default=None, nullable=True)
    parent_id: Mapped[PyUUID|None] = mapped_column(ForeignKey("FileMetadata.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=True, default=None)
    parent: Mapped["FileMetadata"] = relationship("FileMetadata", remote_side=[id])
    children: Mapped[List["FileMetadata"]] = relationship("FileMetadata", uselist=True, back_populates="parent")
    storage_id: Mapped[PyUUID] = mapped_column(ForeignKey("FileStorage.id", onupdate="CASCADE", ondelete="CASCADE"))
    storage: Mapped["FileStorage"] = relationship("FileStorage", foreign_keys=[storage_id], info={"owner": True})
    root_storage_id: Mapped[PyUUID] = mapped_column(ForeignKey("FileStorage.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=True, default=None)
    root_storage: Mapped[Optional["FileStorage"]] = relationship("FileStorage", foreign_keys=[root_storage_id])
    atime_utc: Mapped[datetime] = mapped_column(DateTime)
    mtime_utc: Mapped[datetime] = mapped_column(DateTime)
    ctime_utc: Mapped[datetime] = mapped_column(DateTime)
    access: Mapped[AccessLevel] = mapped_column(SqlEnum(AccessLevel), default=AccessLevel.PRIVATE)

    @property
    def user_id(self) -> PyUUID:
        return self.storage.user_id

    @property
    def user(self) -> User:
        return self.storage.user

    @property
    def total_size(self) -> int:
        return sum(c.total_size for c in self.children) + (self.size or 0)
    
    @property
    def isroot(self) -> bool:
        return self.root_storage_id is not None
    
    @property
    def isfile(self) -> bool:
        return self.type == FileType.FILE

    @property
    def isdir(self) -> bool:
        return self.type == FileType.DIRECTORY

    @property
    def islink(self) -> bool:
        return self.type == FileType.LINK
    
    @property
    def type(self) -> FileType:
        if self.mime_type == DIRECTORY_MIME:
            return FileType.DIRECTORY
        if self.mime_type == LINK_MIME:
            return FileType.LINK
        return FileType.FILE
    
    @property
    def abspath(self) -> str:
        parts = []
        file = self
        while file and not file.isroot:
            parts.append(file.name)
            file = file.parent
        parts.reverse()
        storage_id = self.storage.id
        return fspath.join(storage_id, *parts)
    
    def get_child(self, name) -> Optional["FileMetadata"]:
        if self.islink:
            raise NotImplementedError()
        else:
            target = self
        for child in target.children:
            if child.name == name:
                return child

    def walk(self) -> Generator[Tuple["FileMetadata", List["FileMetadata"], List["FileMetadata"]], None, None]:
        stack: List["FileMetadata"] = [self]
        while stack:
            curr = stack.pop()
            dirs = [c for c in curr.children if c.isdir]
            files = [c for c in curr.children if c.isfile]
            yield curr, dirs, files
            stack.extend(dirs)

    def accessed(self):
        self.atime = datetime.now().astimezone(timezone.utc)

    def modified(self):
        now = datetime.now().astimezone(timezone.utc)
        self.atime = now
        self.mtime = now


class FileStorage(Model):
    __tablename__ = "FileStorage"
    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    user_id: Mapped[PyUUID] = mapped_column(ForeignKey(User.id, onupdate="CASCADE", ondelete="CASCADE"))
    user: Mapped[User] = relationship(User, info={"owner": True})
    name: Mapped[str] = mapped_column(String(512))
    slug: Mapped[str] = mapped_column(String(SLUG_LENGTH), info={"slug": True})
    all_files: Mapped[List[FileMetadata]] = relationship(FileMetadata, uselist=True, back_populates="storage", foreign_keys=[FileMetadata.storage_id])
    root_dir: Mapped[FileMetadata] = relationship(FileMetadata, uselist=False, back_populates="root_storage", foreign_keys=[FileMetadata.root_storage_id])

    @property
    def total_size(self) -> int:
        return self.root_dir.total_size
