from sqlalchemy import delete, select
from typing import List
from uuid import UUID

from core.api.modules.gql import GqlMiniappModule, query, mutation
from core.api.pages import PagesInput, PagesResult
from core.data.sql.columns import ensure_str_fit
from core.graphql.result import SuccessResult

from .data import NotesNote, FileKind, NotesFile
from .collections import ArchivedFilter

from miniapps.files.tools.storage import StorageManager
from miniapps.files.tools.files import FileManager


class NoteAttachmentsModule(GqlMiniappModule):
    STORAGE_NAME = StorageManager.SERVICE_PREFIX + "notes"
    _files: FileManager|None = None

    @property
    def files(self):
        if self._files is None:
            self._files = FileManager.for_service(self.context.files, self.session)
        return self._files
    
    @property
    def storage(self):
        return self.files.storage
    
    @property
    def contents(self):
        return self.files.contents

    @mutation()
    def add_attachment(self, id: UUID, mime_type: str) -> NotesFile:
        statement = select(NotesNote).where(NotesNote.id == id)
        note = self.session.scalars(statement).one()
        note_file = NotesFile(
            note_id=id,
            note=note,
            kind=FileKind.ATTACHMENT,
        )
        self.session.add(note_file)
        self.session.commit()
        storage = self.storage.get_or_create(self.STORAGE_NAME)
        file = self.files.makefile(f"{storage.id}:/{id}/{note_file.id}", mime_type)
        note_file.file_id = file.id
        note_file.file = file
        self.session.commit()
        return note_file

    @mutation()
    def remove_attachment(self, id: UUID, attachment_id: int):
        raise NotImplementedError()