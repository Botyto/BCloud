from typing import List
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from core.asyncjob.context import AsyncJobContext
from core.data.sql.columns import ensure_str_fit

from .files import NoteFileManager

from ..data import NotesNote, NotesCollection, NotesTag


class NotesManager:
    user_id: UUID|None
    context: AsyncJobContext
    session: Session
    service: bool

    _files: NoteFileManager|None = None

    @property
    def files(self) -> NoteFileManager:
        if self._files is None:
            self._files = NoteFileManager(None, self.user_id, self.context, self.session)
        return self._files

    def __init__(self, user_id: UUID|None, context: AsyncJobContext, session: Session, service: bool = False):
        self.user_id = user_id
        self.context = context
        self.session = session
        self.service = service

    @classmethod
    def for_service(cls, user_id: UUID|None, context: AsyncJobContext, session: Session):
        return cls(user_id, context, session, service=True)

    def create(self, collection_id_or_slug: UUID|str, title: str, content: str, tags: List[str]):
        ensure_str_fit("title", title, NotesNote.title)
        ensure_str_fit("content", content, NotesNote.content)
        for tag in tags:
            ensure_str_fit("tag", tag, NotesTag.tag)
        statement = select(NotesCollection)
        if isinstance(collection_id_or_slug, str):
            statement = statement.where(NotesCollection.slug == collection_id_or_slug)
        else:
            statement = statement.where(NotesCollection.id == collection_id_or_slug)
        if self.user_id is not None:
            statement = statement.where(NotesCollection.user_id == self.user_id)
        collection = self.session.scalars(statement).one()
        note = NotesNote(
            collection_id=collection.id,
            collection=collection,
            title=title,
            content=content,
            tags=[NotesTag(tag=tag) for tag in tags],
        )
        self.session.add(note)
        self.session.commit()
        return note
    
    def delete(self, id: UUID):
        note = self.files.delete_all(id)
        title = note.title
        self.session.delete(note)
        return title
    
    def rename(self, id: UUID, title: str):
        ensure_str_fit("title", title, NotesNote.title)
        statement = select(NotesNote).where(NotesNote.id == id)
        if self.user_id is not None:
            statement = statement.where(NotesNote.collection.has(NotesCollection.user_id == self.user_id))
        note = self.session.scalars(statement).one()
        old_title = note.title
        note.title = title
        return old_title, note
    
    def edit(self, id: UUID, content: str):
        ensure_str_fit("content", content, NotesNote.content)
        statement = update(NotesNote) \
            .where(NotesNote.id == id) \
            .values(content=content) \
            .returning(NotesNote)
        if self.user_id is not None:
            statement = statement.where(NotesNote.collection.has(NotesCollection.user_id == self.user_id))
        note = self.session.scalars(statement).one()
        return note
    
    def add_tag(self, id: UUID, tag: str):
        ensure_str_fit("tag", tag, NotesTag.tag)
        statement = select(NotesNote).where(NotesNote.id == id)
        if self.user_id is not None:
            statement = statement.where(NotesNote.collection.has(NotesCollection.user_id == self.user_id))
        note = self.session.scalars(statement).one()
        if tag not in note.tags:
            note.tags.append(NotesTag(tag=tag))
        return note

    def remove_tag(self, id: UUID, tag: str):
        ensure_str_fit("tag", tag, NotesTag.tag)
        statement = select(NotesNote).where(NotesNote.id == id)
        if self.user_id is not None:
            statement = statement.where(NotesNote.collection.has(NotesCollection.user_id == self.user_id))
        note = self.session.scalars(statement).one()
        note.tags = [tag for tag in note.tags if tag.tag != tag]
        return note
    
    def set_favorite(self, id: UUID, favorite: bool) -> NotesNote:
        statement = update(NotesNote) \
            .where(NotesNote.id == id) \
            .values(favorite=favorite) \
            .returning(NotesNote)
        if self.user_id is not None:
            statement = statement.where(NotesNote.collection.has(NotesCollection.user_id == self.user_id))
        note = self.session.scalars(statement).one()
        return note
    
    def set_archived(self, id: UUID, archived: bool) -> NotesNote:
        statement = update(NotesNote) \
            .where(NotesNote.id == id) \
            .values(archived=archived) \
            .returning(NotesNote)
        if self.user_id is not None:
            statement = statement.where(NotesNote.collection.has(NotesCollection.user_id == self.user_id))
        note = self.session.scalars(statement).one()
        return note
    
    def set_sort_key(self, id: UUID, sort_key: float) -> NotesNote:
        statement = update(NotesNote) \
            .where(NotesNote.id == id) \
            .values(sort_key=sort_key) \
            .returning(NotesNote)
        if self.user_id is not None:
            statement = statement.where(NotesNote.collection.has(NotesCollection.user_id == self.user_id))
        note = self.session.scalars(statement).one()
        return note
