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
    def list(self, collection_id: int, archived: ArchivedFilter, pages: PagesInput) -> PagesResult[NotesNote]:
        statement = select(NotesNote).where(NotesNote.collection_id == collection_id)
        statement = archived.filter(statement)
        return pages.of(self.session, statement)

    @query()
    def search(self, tag: str, archived: ArchivedFilter, pages: PagesInput) -> PagesResult[NotesNote]:
        statement = select(NotesNote).where(NotesNote.tags.any(NotesTag.tag == tag))
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
    def edit(self,
        id: UUID,
        title: str|None,
        content: str|None,
        tags: List[str]|None,
        favorite: bool|None,
        archived: bool|None,
        sort_key: float|None,
    ) -> NotesNote:
        if all(arg is None for arg in (title, content, tags, favorite, archived, sort_key)):
            raise ValueError("Nothing to edit")
        # validate strings
        if title is not None:
            ensure_str_fit("title", title, NotesNote.title)
        if content is not None:
            ensure_str_fit("content", content, NotesNote.content)
        if tags:
            for tag in tags:
                ensure_str_fit("tag", tag, NotesTag.tag)
        # edit
        statement = select(NotesNote).where(NotesNote.id == id)
        note = self.session.scalars(statement).one()
        if title is not None:
            note.title = title
        if content is not None:
            note.content = content
        if tags is not None:
            # TODO optimize tag replacement
            note.tags = [NotesTag(tag=tag) for tag in tags]
        if favorite is not None:
            note.favorite = favorite
        if archived is not None:
            note.archived = archived
        if sort_key is not None:
            note.sort_key = sort_key
        self.session.commit()
        self.log_activity("note.edit", {"id": str(id), "title": note.title})
        return note
