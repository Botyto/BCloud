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
from .tools.notes import NotesManager


class NotesModule(GqlMiniappModule):
    _notes: NotesManager|None = None

    @property
    def notes(self):
        if self._notes is None:
            self._notes = NotesManager(self.user_id, self.context, self.session)
        return self._notes

    def _list(self, collection_id_or_slug: UUID|str, archived: ArchivedFilter, tag: str|None, pages: PagesInput) -> PagesResult[NotesNote]:
        statement = select(NotesNote)
        if isinstance(collection_id_or_slug, str):
            statement = statement \
                .where(NotesNote.collection.has(NotesCollection.slug == collection_id_or_slug)) \
                .options(joinedload(NotesNote.collection))
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
        note = self.notes.create(collection_id_or_slug, title, content, tags)
        self.log_activity("note.create", {"id": str(note.id), "title": title, "collection_id": str(note.collection_id)})
        return note
    
    @mutation()
    def create_with_id(self, collection_id: UUID, title: str, content: str, tags: List[str]) -> NotesNote:
        return self._create(collection_id, title, content, tags)

    @mutation()
    def create_with_slug(self, collection_slug: str, title: str, content: str, tags: List[str]) -> NotesNote:
        return self._create(collection_slug, title, content, tags)

    @mutation()
    def delete(self, id: UUID) -> SuccessResult:
        title = self.notes.delete(id)
        self.log_activity("note.delete", {"id": str(id), "title": title})
        return SuccessResult()

    @mutation()
    def rename(self, id: UUID, title: str) -> NotesNote:
        old_title, note = self.notes.rename(id, title)
        self.log_activity("note.rename", {"id": str(id), "old": old_title, "new": title})
        return note
    
    @mutation()
    def edit(self, id: UUID, title: str, content: str) -> NotesNote:
        note = self.notes.edit(id, title, content)
        self.log_activity("note.edit", {"id": str(id), "title": note.title})
        return note
    
    @mutation()
    def add_tag(self, id: UUID, tag: str) -> NotesNote:
        note = self.notes.add_tag(id, tag)
        self.log_activity("note.add_tag", {"id": str(id), "title": note.title, "tag": tag})
        return note
    
    @mutation()
    def remove_tag(self, id: UUID, tag: str) -> NotesNote:
        note = self.notes.remove_tag(id, tag)
        self.log_activity("note.remove_tag", {"id": str(id), "title": note.title, "tag": tag})
        return note
    
    @mutation()
    def set_favorite(self, id: UUID, favorite: bool) -> NotesNote:
        note = self.notes.set_favorite(id, favorite)
        self.log_activity("note.set_favorite", {"id": str(id), "title": note.title, "favorite": favorite})
        return note
    
    @mutation()
    def set_archived(self, id: UUID, archived: bool) -> NotesNote:
        note = self.notes.set_archived(id, archived)
        self.log_activity("note.set_archived", {"id": str(id), "title": note.title, "archived": archived})
        return note
    
    @mutation()
    def set_sort_key(self, id: UUID, sort_key: float) -> NotesNote:
        note = self.notes.set_sort_key(id, sort_key)
        # self.log_activity("note.set_sort_key", {"id": str(id), "sort_key": note.sort_key})
        return note
