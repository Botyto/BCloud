from sqlalchemy import select
from sqlalchemy.orm import joinedload
from uuid import UUID

from core.asyncjob.context import AsyncJobContext
from core.data.sql.database import Session

from miniapps.files.data import FileStorage
from miniapps.files.tools import fspath
from miniapps.files.tools.contents import FileContents, NAMESPACE_CONTENT
from miniapps.files.tools.files import FileManager
from miniapps.files.tools.storage import StorageManager

from ..data import NotesNote, NotesFileKind, NotesFile, NotesCollection


class NoteFileManager:
    STORAGE_NAME = StorageManager.SERVICE_PREFIX + "notes"

    kind: NotesFileKind|None
    user_id: UUID|None
    context: AsyncJobContext
    service: bool
    _session: Session|None = None
    _files: FileManager|None = None
    _contents: FileContents|None = None

    @property
    def files(self):
        if self._files is None:
            if self.user_id:
                self._files = FileManager(self.context.blobs, self.user_id, self.session, service=True)
            else:
                self._files = FileManager.for_service(self.context.blobs, self.session)
        return self._files
    
    @property
    def contents(self):
        if self._contents is None:
            self._contents = FileContents(self.context.blobs, NAMESPACE_CONTENT)
        return self._contents
    
    @property
    def session(self):
        if self._session is None:
            self._session = self.context.database.make_session()
        return self._session

    def __init__(self, kind: NotesFileKind|None, user_id: UUID|None, context: AsyncJobContext, session: Session, service: bool =False):
        self.user_id = user_id
        self.kind = kind
        self.context = context
        self._session = session
        self.service = service

    @classmethod
    def for_service(cls, kind: NotesFileKind|None, user_id: UUID|None, context: AsyncJobContext, session: Session):
        return cls(kind, user_id, context, session, service=True)
    
    def _folder_path(self, storage: FileStorage, note: NotesNote):
        return fspath.join(storage.id, str(note.id))

    def _file_path(self, storage: FileStorage, note: NotesNote, note_file: NotesFile) -> str:
        return fspath.join(storage.id, str(note.id), str(note_file.id))
    
    def _get_note(self, note: UUID|NotesNote) -> NotesNote|None:
        if isinstance(note, UUID):
            statement = select(NotesNote) \
                .filter(NotesNote.id == note)
            if self.user_id is not None:
                statement = statement.filter(NotesNote.collection.has(NotesCollection.user_id == self.user_id))
            return self.session.scalars(statement).one_or_none()
        return note

    def default_get(self, note: UUID|NotesNote, kind: NotesFileKind|None = None) -> NotesFile|None:
        if kind is None:
            kind = self.kind
        assert kind is not None, "Kind is not set"
        note_id = note if isinstance(note, UUID) else note.id
        statement = select(NotesFile) \
            .filter(NotesFile.note_id == note_id, NotesFile.kind == self.kind) \
            .options(joinedload(NotesFile.file))
        if self.user_id is not None:
            statement = statement.filter(NotesFile.note.has(NotesNote.collection.has(NotesCollection.user_id == self.user_id)))
        return self.session.scalars(statement).first()
    
    def default_write(self, note: UUID|NotesNote, content: bytes|None, mime_type: str, kind: NotesFileKind|None = None) -> NotesFile:
        if kind is None:
            kind = self.kind
        assert kind is not None, "Kind is not set"
        note_obj = self._get_note(note)
        if note_obj is None:
            raise ValueError("Note not found")
        note_file = self.default_get(note_obj.id, kind)
        if note_file is None:
            note_file = NotesFile(
                note_id=note_obj.id,
                kind=kind,
            )
            storage = self.files.storage.get_or_create(self.STORAGE_NAME)
            if self.session.is_modified(storage):
                self.session.commit()
            path = self._file_path(storage, note_obj, note_file)
            file = self.files.makefile(path, mime_type, make_dirs=True)
            note_file.file = file
            self.session.add(note_file)
            self.session.add(file)
            self.session.commit()
        else:
            file = note_file.file
        self.contents.write(file, content, mime_type)
        return note_file
    
    def default_delete(self, note: UUID|NotesNote, kind: NotesFileKind|None) -> NotesFile|None:
        note_file = self.default_get(note, kind)
        return self.delete(note_file)
    
    def __delete_nocommit(self, note_file: UUID|NotesFile|None) -> NotesFile|None:
        note_file_obj: NotesFile|None
        if isinstance(note_file, UUID):
            statement = select(NotesFile) \
                .filter(NotesFile.id == note_file) \
                .options(joinedload(NotesFile.file))
            if self.user_id is not None:
                statement = statement.filter(NotesFile.note.has(NotesNote.collection.has(NotesCollection.user_id == self.user_id)))
            note_file_obj = self.session.scalars(statement).one()
        else:
            note_file_obj = note_file
        if note_file_obj is None:
            return
        self.contents.delete(note_file_obj.file)
        self.session.delete(note_file_obj.file)
        self.session.delete(note_file_obj)
        return note_file_obj
    
    def __delete_empty_folder(self, note: NotesNote, autocommit: bool = True):
        if note.files:
            return
        storage = self.files.storage.by_name(self.STORAGE_NAME)
        if storage is None:
            return
        path = self._folder_path(storage, note)
        self.files.delete(path)
        if autocommit:
            self.session.commit()

    def delete(self, note_file: UUID|NotesFile|None) -> NotesFile|None:
        note_file_obj = self.__delete_nocommit(note_file)
        if note_file_obj is not None:
            note_obj = note_file_obj.note
            self.__delete_empty_folder(note_obj, autocommit=False)
            self.session.commit()
        return note_file_obj
    
    def delete_all(self, note: UUID|NotesNote) -> NotesNote:
        if isinstance(note, NotesNote):
            note_obj = note
        else:
            statement = select(NotesNote) \
                .filter(NotesNote.id == note) \
                .options(joinedload(NotesNote.files))
            if self.user_id is not None:
                statement = statement.filter(NotesNote.collection.has(NotesCollection.user_id == self.user_id))
            note_obj = self.session.scalars(statement).unique().one()
        for file in note_obj.files:
            self.__delete_nocommit(file)
        self.session.commit()
        self.__delete_empty_folder(note_obj)
        return note_obj
