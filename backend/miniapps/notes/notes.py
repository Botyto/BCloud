from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List
from uuid import UUID

from core.api.modules.gql import GqlMiniappModule, query, mutation
from core.api.pages import PagesInput, PagesResult
from core.data.sql.columns import ensure_str_fit
from core.graphql.result import SuccessResult

from .collections import ArchivedFilter
from .data import NotesCollection, NotesNote, NotesTag
from .tools.files import NoteFileManager


class NotesModule(GqlMiniappModule):
    def _list(self, collection_id_or_slug: UUID|str, archived: ArchivedFilter, tag: str|None, pages: PagesInput) -> PagesResult[NotesNote]:
        statement = select(NotesNote)
        if isinstance(collection_id_or_slug, str):
            statement = statement \
                .options(joinedload(NotesNote.collection)) \
                .where(NotesCollection.slug == collection_id_or_slug)
        else:
            statement = statement.where(NotesNote.collection_id == collection_id_or_slug)
        if tag is not None:
            statement = statement.where(NotesNote.tags.any(NotesTag.tag == tag))
        statement = archived.filter(statement)
        return pages.of(self.session, statement)

    @query()
    def list_by_id(self, collection_id: UUID, archived: ArchivedFilter, tag: str|None, pages: PagesInput) -> PagesResult[NotesNote]:
        return self._list(collection_id, archived, tag, pages)
    
    @query()
    def list_by_slug(self, collection_slug: str, archived: ArchivedFilter, tag: str|None, pages: PagesInput) -> PagesResult[NotesNote]:
        return self._list(collection_slug, archived, tag, pages)

    def _create(self, collection_id_or_slug: UUID|str, title: str, content: str, tags: List[str]) -> NotesNote:
        ensure_str_fit("title", title, NotesNote.title)
        ensure_str_fit("content", content, NotesNote.content)
        for tag in tags:
            ensure_str_fit("tag", tag, NotesTag.tag)
        statement = select(NotesCollection)
        if isinstance(collection_id_or_slug, str):
            statement = statement.where(NotesCollection.slug == collection_id_or_slug)
        else:
            statement = statement.where(NotesCollection.id == collection_id_or_slug)
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
        self.log_activity("note.create", {"id": str(note.id), "title": title, "collection_id": str(collection.id)})
        return note
    
    @mutation()
    def create_with_id(self, collection_id: UUID, title: str, content: str, tags: List[str]) -> NotesNote:
        return self._create(collection_id, title, content, tags)

    @mutation()
    def create_with_slug(self, collection_slug: str, title: str, content: str, tags: List[str]) -> NotesNote:
        return self._create(collection_slug, title, content, tags)

    @mutation()
    def delete(self, id: UUID) -> SuccessResult:
        files = NoteFileManager(None, self.user_id, self.context, self.session)
        note = files.delete_all(id)
        title = note.title
        self.session.delete(note)
        self.log_activity("note.delete", {"id": str(id), "title": title})
        return SuccessResult()

    @mutation()
    def rename(self, id: UUID, title: str) -> NotesNote:
        ensure_str_fit("title", title, NotesNote.title)
        statement = select(NotesNote).where(NotesNote.id == id)
        note = self.session.scalars(statement).one()
        note.title = title
        self.log_activity("note.rename", {"id": str(id), "title": title})
        return note
    
    @mutation()
    def edit(self, id: UUID, content: str) -> NotesNote:
        ensure_str_fit("content", content, NotesNote.content)
        statement = select(NotesNote).where(NotesNote.id == id)
        note = self.session.scalars(statement).one()
        note.content = content
        self.log_activity("note.edit", {"id": str(id), "title": note.title})
        return note
    
    @mutation()
    def add_tag(self, id: UUID, tag: str) -> NotesNote:
        ensure_str_fit("tag", tag, NotesTag.tag)
        statement = select(NotesNote).where(NotesNote.id == id)
        note = self.session.scalars(statement).one()
        if tag in note.tags:
            return note
        note.tags.append(NotesTag(tag=tag))
        self.log_activity("note.add_tag", {"id": str(id), "title": note.title, "tag": tag})
        return note
    
    @mutation()
    def remove_tag(self, id: UUID, tag: str) -> NotesNote:
        ensure_str_fit("tag", tag, NotesTag.tag)
        statement = select(NotesNote).where(NotesNote.id == id)
        note = self.session.scalars(statement).one()
        note.tags = [tag for tag in note.tags if tag.tag != tag]
        self.log_activity("note.remove_tag", {"id": str(id), "title": note.title, "tag": tag})
        return note
    
    @mutation()
    def set_favorite(self, id: UUID, favorite: bool) -> NotesNote:
        statement = select(NotesNote).where(NotesNote.id == id)
        note = self.session.scalars(statement).one()
        note.favorite = favorite
        self.log_activity("note.set_favorite", {"id": str(id), "title": note.title, "favorite": favorite})
        return note
    
    @mutation()
    def set_archived(self, id: UUID, archived: bool) -> NotesNote:
        statement = select(NotesNote).where(NotesNote.id == id)
        note = self.session.scalars(statement).one()
        note.archived = archived
        self.log_activity("note.set_archived", {"id": str(id), "title": note.title, "archived": archived})
        return note
    
    @mutation()
    def set_sort_key(self, id: UUID, sort_key: float) -> NotesNote:
        statement = select(NotesNote).where(NotesNote.id == id)
        note = self.session.scalars(statement).one()
        note.sort_key = sort_key
        # self.log_activity("note.set_sort_key", {"id": str(id), "sort_key": note.sort_key})
        return note
