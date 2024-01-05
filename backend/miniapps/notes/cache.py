from dataclasses import dataclass
import re
import requests

from .background import NotePostprocessor
from .data import NotesNote
from .tools.files import NoteFileManager, FileKind


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

    _precached: bool = False
    _url: str|None = None

    def precache(self):
        if self._precached:
            return
        self._precached = True
        self._url = self.extract_url(self.note)

    def extract_url(self, note: NotesNote) -> str|None:
        if self.URL_PATTERN_FULL.match(note.content):
            return note.content
        
    def should_run(self):
        self.precache()
        return bool(self._url)
    
    def prerender(self, cache: HtmlCache):
        return cache  # TODO implement

    def run(self):
        assert self._precached, "precache() should be called before run()"
        assert self._url is not None
        cacher = HtmlChacher()
        cache = cacher.cache(self._url)
        if cache is None:
            return
        if cache.mime_type == "text/html":
            cache = self.prerender(cache)
        user_id = self.note.collection.user_id
        files = NoteFileManager(FileKind.CACHE, user_id, self.context, self.session)
        files.default_write(self.note_id, cache.content, cache.mime_type)
