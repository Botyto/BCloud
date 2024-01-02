import re
from sqlalchemy import select
from uuid import UUID

from core.asyncjob.handlers import AsyncJobHandler

from .data import NotesNote, FileKind
from .cache import HtmlChacher
from .tools.files import NoteFileManager


class CacheHandler(AsyncJobHandler):
    URL_PATTERN = re.compile(r"https?://[^\s]+")
    URL_PATTERN_FULL = re.compile(r"^https?://[^\s]+$")

    def __extract_url(self, note: NotesNote) -> str|None:
        if self.URL_PATTERN_FULL.match(note.content):
            return note.content

    def run(self):
        note_id = UUID(self.context.get_payload("id"))
        with self.context.database.make_session() as session:
            statement = select(NotesNote).filter(NotesNote.id == note_id).join(NotesNote.collection)
            note = session.scalars(statement).one_or_none()
            if note is None:
                return
            user_id = note.collection.user_id
            url = self.__extract_url(note)
            if url is None:
                return
        cacher = HtmlChacher()
        cache = cacher.cache(url)
        if cache is None:
            return
        with self.context.database.make_session() as session:
            files = NoteFileManager(FileKind.CACHE, user_id, self.context, session)
            files.default_write(note_id, cache.content, cache.mime_type)
