import re
from sqlalchemy import select
from uuid import UUID

from core.asyncjob.handlers import AsyncJobHandler

from miniapps.files.tools.files import FileManager
from miniapps.files.tools.storage import StorageManager

from .data import NotesNote, NotesFile
from .cache import HtmlChacher


class CacheHandler(AsyncJobHandler):
    URL_PATTERN = re.compile(r"https?://[^\s]+")
    URL_PATTERN_FULL = re.compile(r"^https?://[^\s]+$")

    def __extract_url(self, note: NotesNote) -> str|None:
        if self.URL_PATTERN_FULL.match(note.content):
            return note.content

    def run(self):
        id = UUID(self.context.get_payload("id"))
        with self.context.database.make_session() as session:
            statement = select(NotesNote).filter(NotesNote.id == id)
            note = session.scalars(statement).one_or_none()
            if note is None:
                return
            url = self.__extract_url(note)
            if url is None:
                return
        cacher = HtmlChacher()
        cache = cacher.cache(url)
        if not cache:
            return
        with self.context.database.make_session() as session:
            files = FileManager.for_service(self.context.files, session)
            storage = files.storage.get_or_create(StorageManager.SERVICE_PREFIX + "notes")
            files.makefile()
