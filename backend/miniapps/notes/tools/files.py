from sqlalchemy import select
from uuid import UUID

from core.asyncjob.context import AsyncJobContext
from core.data.sql.database import Session

from miniapps.files.data import FileStorage
from miniapps.files.tools.contents import FileContents, NAMESPACE_CONTENT
from miniapps.files.tools.files import FileManager
from miniapps.files.tools.storage import StorageManager

from ..data import NotesNote, FileKind, NotesFile, NotesCollection


class NoteFileManager:
    STORAGE_NAME = StorageManager.SERVICE_PREFIX + "notes"

    kind: FileKind
    context: AsyncJobContext
    service: bool
    _session: Session|None = None
    _files: FileManager|None = None
    _contents: FileContents|None = None

    @property
    def files(self):
        if self._files is None:
            self._files = FileManager.for_service(self.context.files, self.session)
        return self._files
    
    @property
    def contents(self):
        if self._contents is None:
            self._contents = FileContents(self.context.files, NAMESPACE_CONTENT)
        return self._contents
    
    @property
    def session(self):
        if self._session is None:
            self._session = self.context.database.make_session()
        return self._session

    def __init__(self, kind: FileKind, context: AsyncJobContext, session: Session, service: bool =False):
        self.kind = kind
        self.context = context
        self.service = service

    @classmethod
    def for_service(cls, kind: FileKind, context: AsyncJobContext, session: Session):
        return cls(kind, context, session, service=True)
    
    def _file_path(self, storage: FileStorage, note: NotesNote, note_file: NotesFile) -> str:
        return f"{storage.id}:/{note.id}/{note_file.id}"
    
    def _get_note(self, note_id: UUID) -> NotesNote|None:
        statement = select(NotesNote) \
            .filter(NotesNote.id == note_id)
        if self.user_id is not None:
            statement = statement.filter(NotesNote.collection.has(NotesCollection.user_id == self.user_id))
        return self.session.scalars(statement).one_or_none()

    def default_get(self, note_id: UUID) -> NotesFile|None:
        statement = select(NotesFile) \
            .filter(NotesFile.note_id == note_id, NotesFile.kind == self.kind) \
            .join(NotesFile.file)
        return self.session.scalars(statement).one_or_none()
    
    def default_write(self, note_id: UUID, content: bytes, mime_type: str) -> NotesFile:
        note = self._get_note(note_id)
        if note is None:
            raise ValueError("Note not found")
        note_file = self.default_get(note_id)
        if note_file is None:
            note_file = NotesFile(
                note_id=note_id,
                kind=self.kind,
            )
            storage = self.files.storage.get_or_create(self.STORAGE_NAME)
            if self.session.is_modified(storage):
                self.session.commit()
            path = self._file_path(storage, note, note_file)
            file = self.files.makefile(path, mime_type)
            note_file.file = file
            self.session.add(note_file)
            self.session.add(file)
            self.session.commit()
        else:
            file = note_file.file
        self.contents.write(file, content)
        return note_file
    
    def default_delete(self, note_id: UUID):
        note_file = self.default_get(note_id)
        if note_file is None:
            return
        self.contents.delete(note_file.file)
        self.session.delete(note_file.file)
        self.session.delete(note_file)
        self.session.commit()
