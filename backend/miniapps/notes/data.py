from enum import Enum as PyEnum
from datetime import datetime
from sqlalchemy import ForeignKey
from typing import List
from uuid import UUID as PyUUID, uuid4

from core.auth.data import User
from core.data.sql.columns import Boolean, DateTime, Enum, Float, Integer, String, UUID, STRING_MAX, utcnow_tz
from core.data.sql.columns import mapped_column, relationship, Mapped
from core.data.sql.database import Model
from core.data.sql.slugs import SLUG_LENGTH

from miniapps.files.data import FileMetadata


class NotesNote(Model):
    __tablename__ = "NotesNote"
    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    collection_id: Mapped[int] = mapped_column(ForeignKey("NotesCollection.id", onupdate="CASCADE", ondelete="CASCADE"))
    collection: Mapped["NotesCollection"] = relationship("NotesCollection", info={"owner": True})
    created_at_utc: Mapped[datetime] = mapped_column(DateTime, default=utcnow_tz)
    slug: Mapped[str] = mapped_column(String(SLUG_LENGTH), info={"slug": True})
    sort_key: Mapped[float] = mapped_column(Float, default=0.0)
    title: Mapped[str] = mapped_column(String(4096))
    content: Mapped[str] = mapped_column(String(STRING_MAX))
    favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    tags: Mapped[List["NotesTag"]] = relationship("NotesTag", uselist=True, back_populates="note")
    preview_id: Mapped[PyUUID] = mapped_column(UUID, ForeignKey("FileMetadata.id", onupdate="CASCADE", ondelete="CASCADE"))
    preview: Mapped["FileMetadata"] = relationship("FileMetadata", foreign_keys=[preview_id])


class NotesTag(Model):
    __tablename__ = "NotesTag"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    note_id: Mapped[PyUUID] = mapped_column(ForeignKey(NotesNote.id, onupdate="CASCADE", ondelete="CASCADE"))
    note: Mapped[NotesNote] = relationship(NotesNote, info={"owner": True})
    tag: Mapped[str] = mapped_column(String(128))


class CollectionView(PyEnum):
    NOTES = "notes"
    LINKS = "links"
    STREAM = "stream"


class NotesCollection(Model):
    __tablename__ = "NotesCollection"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[PyUUID] = mapped_column(ForeignKey("User.id", onupdate="CASCADE", ondelete="CASCADE"))
    user: Mapped[User] = relationship(User, info={"owner": True})
    created_at_utc: Mapped[datetime] = mapped_column(DateTime, default=utcnow_tz)
    parent_id: Mapped[int|None] = mapped_column(Integer, ForeignKey("NotesCollection.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=True, default=None)
    parent: Mapped["NotesCollection"|None] = relationship("NotesCollection", remote_side=[id])
    children: Mapped[List["NotesCollection"]] = relationship("NotesCollection", uselist=True, back_populates="parent")
    slug: Mapped[str] = mapped_column(String(SLUG_LENGTH), info={"slug": True})
    name: Mapped[str] = mapped_column(String(128))
    view: Mapped[CollectionView] = mapped_column(Enum(CollectionView), default=CollectionView.NOTES.value)
