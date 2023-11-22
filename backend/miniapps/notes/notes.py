from sqlalchemy import delete, select
from typing import List
from uuid import UUID

from core.api.modules.gql import GqlMiniappModule, query, mutation
from core.api.pages import PagesInput, PagesResult
from core.data.sql.columns import ensure_str_fit
from core.graphql.result import SuccessResult

from .data import NotesCollection, NotesNote, NotesTag
from .collections import ArchivedFilter


class NotesModule(GqlMiniappModule):
    @query()
    def list(self, collection_id: int, archived: ArchivedFilter, tag: str|None, pages: PagesInput) -> PagesResult[NotesNote]:
        statement = select(NotesNote).where(NotesNote.collection_id == collection_id)
        if tag is not None:
            statement = statement.where(NotesNote.tags.any(NotesTag.tag == tag))
        statement = archived.filter(statement)
        return pages.of(self.session, statement)

    @mutation()
    def create(self, collection_id: int, title: str, content: str, tags: List[str]) -> NotesNote:
        ensure_str_fit("title", title, NotesNote.title)
        ensure_str_fit("content", content, NotesNote.content)
        for tag in tags:
            ensure_str_fit("tag", tag, NotesTag.tag)
        statement = select(NotesCollection).where(NotesCollection.id == collection_id)
        collection = self.session.scalars(statement).one()
        note = NotesNote(
            collection_id=collection_id,
            collection=collection,
            title=title,
            content=content,
            tags=[NotesTag(tag=tag) for tag in tags],
        )
        self.session.add(note)
        self.session.commit()
        self.log_activity("note.create", {"id": str(note.id), "title": title, "collection_id": collection_id})
        return note

    @mutation()
    def delete(self, id: UUID) -> SuccessResult:
        statement = delete(NotesNote) \
            .where(NotesNote.id == id) \
            .returning(NotesNote.title)
        result = self.session.execute(statement)
        title = result.scalar_one()
        self.log_activity("collection.delete", {"id": str(id), "title": title})
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
    def edit(self, id: UUID, content: str):
        ensure_str_fit("content", content, NotesNote.content)
        statement = select(NotesNote).where(NotesNote.id == id)
        note = self.session.scalars(statement).one()
        note.content = content
        self.log_activity("note.edit", {"id": str(id), "title": note.title})
        return note
    
    @mutation()
    def add_tag(self, id: UUID, tag: str):
        ensure_str_fit("tag", tag, NotesTag.tag)
        statement = select(NotesNote).where(NotesNote.id == id)
        note = self.session.scalars(statement).one()
        if tag in note.tags:
            return note
        note.tags.append(NotesTag(tag=tag))
        self.log_activity("note.add_tag", {"id": str(id), "title": note.title, "tag": tag})
        return note
    
    @mutation()
    def remove_tag(self, id: UUID, tag: str):
        ensure_str_fit("tag", tag, NotesTag.tag)
        statement = select(NotesNote).where(NotesNote.id == id)
        note = self.session.scalars(statement).one()
        note.tags = [tag for tag in note.tags if tag.tag != tag]
        self.log_activity("note.remove_tag", {"id": str(id), "title": note.title, "tag": tag})
        return note
    
    @mutation()
    def set_favorite(self, id: UUID, favorite: bool):
        statement = select(NotesNote).where(NotesNote.id == id)
        note = self.session.scalars(statement).one()
        note.favorite = favorite
        self.log_activity("note.set_favorite", {"id": str(id), "title": note.title, "favorite": favorite})
        return note
    
    @mutation()
    def set_archived(self, id: UUID, archived: bool):
        statement = select(NotesNote).where(NotesNote.id == id)
        note = self.session.scalars(statement).one()
        note.archived = archived
        self.log_activity("note.set_archived", {"id": str(id), "title": note.title, "archived": archived})
        return note
    
    @mutation()
    def set_sort_key(self, id: UUID, sort_key: float):
        statement = select(NotesNote).where(NotesNote.id == id)
        note = self.session.scalars(statement).one()
        note.sort_key = sort_key
        return note
