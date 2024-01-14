from enum import Enum as PyEnum
from datetime import datetime
from sqlalchemy import ForeignKey
from typing import List, Optional
from uuid import UUID as PyUUID, uuid4

from core.auth.access import AccessLevel, access_info
from core.auth.data import User
from core.auth.owner import owner_info
from core.data.sql.columns import Boolean, DateTime, Enum, Float, Integer, String, UUID, STRING_MAX, utcnow_tz
from core.data.sql.columns import mapped_column, relationship, Mapped
from core.data.sql.database import Model
from core.data.sql.slugs import SLUG_LENGTH, slug_info

from miniapps.files.data import FileMetadata


class NotesNote(Model):
    __tablename__ = "NotesNote"
    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    collection_id: Mapped[PyUUID] = mapped_column(ForeignKey("NotesCollection.id", onupdate="CASCADE", ondelete="CASCADE"))
    collection: Mapped["NotesCollection"] = relationship("NotesCollection", info=owner_info(), back_populates="notes")
    created_at_utc: Mapped[datetime] = mapped_column(DateTime, default=utcnow_tz)
    slug: Mapped[str] = mapped_column(String(SLUG_LENGTH), info=slug_info())
    sort_key: Mapped[float] = mapped_column(Float, default=0.0)
    title: Mapped[str] = mapped_column(String(4096))
    content: Mapped[str] = mapped_column(String(STRING_MAX))
    favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    color: Mapped[str] = mapped_column(String(32), default="#dddddd")
    tags: Mapped[List["NotesTag"]] = relationship("NotesTag", uselist=True, back_populates="note")
    files: Mapped[List["NotesFile"]] = relationship("NotesFile", uselist=True, back_populates="note")


class NotesFileKind(PyEnum):
    ATTACHMENT = "attachment"
    PREVIEW = "preview"
    CACHE = "cache"


class NotesFile(Model):
    __tablename__ = "NotesFile"
    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    note_id: Mapped[PyUUID] = mapped_column(ForeignKey(NotesNote.id, onupdate="CASCADE", ondelete="CASCADE"))
    note: Mapped[NotesNote] = relationship(NotesNote, info=owner_info(), back_populates="files")
    kind: Mapped[NotesFileKind] = mapped_column(Enum(NotesFileKind))
    file_id: Mapped[PyUUID] = mapped_column(ForeignKey("FileMetadata.id", onupdate="CASCADE", ondelete="CASCADE"))
    file: Mapped["FileMetadata"] = relationship("FileMetadata", foreign_keys=[file_id])


class NotesTag(Model):
    __tablename__ = "NotesTag"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    note_id: Mapped[PyUUID] = mapped_column(ForeignKey(NotesNote.id, onupdate="CASCADE", ondelete="CASCADE"))
    note: Mapped[NotesNote] = relationship(NotesNote, info=owner_info(), back_populates="tags")
    tag: Mapped[str] = mapped_column(String(128))


class NotesCollectionView(PyEnum):
    NOTES = "notes"
    BOOKMARKS = "bookmarks"
    CHAT = "chat"


class NotesCollection(Model):
    __tablename__ = "NotesCollection"
    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    user_id: Mapped[PyUUID] = mapped_column(ForeignKey("User.id", onupdate="CASCADE", ondelete="CASCADE"))
    user: Mapped[User] = relationship(User, info=owner_info())
    created_at_utc: Mapped[datetime] = mapped_column(DateTime, default=utcnow_tz)
    parent_id: Mapped[PyUUID|None] = mapped_column(ForeignKey("NotesCollection.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=True, default=None)
    parent: Mapped[Optional["NotesCollection"]] = relationship("NotesCollection", remote_side=[id])
    children: Mapped[List["NotesCollection"]] = relationship("NotesCollection", uselist=True, back_populates="parent")
    slug: Mapped[str] = mapped_column(String(SLUG_LENGTH), info=slug_info())
    name: Mapped[str] = mapped_column(String(128))
    view: Mapped[NotesCollectionView] = mapped_column(Enum(NotesCollectionView), default=NotesCollectionView.NOTES.value)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    access: Mapped[AccessLevel] = mapped_column(Enum(AccessLevel), default=AccessLevel.PRIVATE, info=access_info())
    notes: Mapped[List[NotesNote]] = relationship("NotesNote", uselist=True, back_populates="collection")
