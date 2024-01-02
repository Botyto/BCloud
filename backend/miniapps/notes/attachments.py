from sqlalchemy import select
from uuid import UUID, uuid4

from core.api.modules.gql import GqlMiniappModule, mutation

from .data import NotesNote, FileKind, NotesFile

from miniapps.files.tools.storage import StorageManager
from miniapps.files.tools.files import FileManager


class NoteAttachmentsModule(GqlMiniappModule):
    STORAGE_NAME = StorageManager.SERVICE_PREFIX + "notes"
    
    @mutation()
    def add_attachment(self, note_id: UUID, kind: FileKind, mime_type: str) -> NotesFile:
        statement = select(NotesNote).where(NotesNote.id == note_id)
        note = self.session.scalars(statement).one()
        note_file = NotesFile(
            id=uuid4(),
            note_id=note_id,
            note=note,
            kind=kind,
        )
        files = FileManager(self.context.blobs, note.collection.user_id, self.session, service=True)
        storage = files.storage.get_or_create(self.STORAGE_NAME)
        files.makedirs(f"{storage.id}:/{note_id}")
        self.session.commit()
        file = files.makefile(f"{storage.id}:/{note_id}/{note_file.id}", mime_type)
        note_file.file_id = file.id
        note_file.file = file
        self.session.add(note_file)
        self.session.commit()
        return note_file

    @mutation()
    def remove_attachment(self, note_id: UUID, attachment_id: int) -> NotesNote:
        raise NotImplementedError()