from dataclasses import dataclass
import re
import requests
from uuid import UUID

from sqlalchemy import select

from .data import NotesNote
from .tools.files import NoteFileManager, FileKind
from .background import NotePostprocessor


@dataclass
class HtmlCache:
    mime_type: str
    content: bytes


class HtmlChacher:
    def cache(self, url: str) -> HtmlCache|None:
        response = requests.get(url)
        if response.text:
            mime_type = response.headers.get("Content-Type", "text/html")
            content = response.content
            return HtmlCache(mime_type, content)


class HtmlCachePostprocessor(NotePostprocessor):
    URL_PATTERN = re.compile(r"https?://[^\s]+")
    URL_PATTERN_FULL = re.compile(r"^https?://[^\s]+$")

    _note_id: UUID|None = None
    _url: str|None = None
    _user_id: UUID|None = None

    def precache(self):
        if self._note_id is not None:
            return
        with self.context.database.make_session() as session:
            self._note_id = self.context.get_payload("note_id")
            statement = select(NotesNote) \
                .filter(NotesNote.id == self._note_id) \
                .join(NotesNote.collection)
            note = session.scalars(statement).first()
            if note is None:
                return
            self._user_id = note.collection.user_id
            self._url = self.extract_url(note)

    def extract_url(self, note: NotesNote) -> str|None:
        if self.URL_PATTERN_FULL.match(note.content):
            return note.content
        
    def should_run(self):
        self.precache()
        return bool(self._url)

    def run(self):
        assert self._note_id is not None, "precache() should be called before run()"
        cacher = HtmlChacher()
        cache = cacher.cache(self._url)  # type: ignore
        if cache is None:
            return
        with self.context.database.make_session() as session:
            files = NoteFileManager(FileKind.CACHE, self._user_id, self.context, session)
            files.default_write(self._note_id, cache.content, cache.mime_type)  # type: ignore
