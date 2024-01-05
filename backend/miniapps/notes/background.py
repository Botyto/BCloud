from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import Session

from core.asyncjob.context import AsyncJobRuntimeContext
from core.asyncjob.handlers import AsyncJobHandler

from .data import NotesNote


class NotePostprocessorContext(AsyncJobRuntimeContext):
    session: Session
    _note_id: UUID|None = None
    _note: NotesNote|None = None

    @property
    def note_id(self) -> UUID:
        if self._note_id is None:
            self._note_id = UUID(self.get_payload("note_id"))
        return self._note_id

    @property
    def note(self) -> NotesNote:
        if self._note is None:
            statement = select(NotesNote) \
                .where(NotesNote.id == self.note_id) \
                .options(joinedload(NotesNote.collection, NotesNote.tags, NotesNote.files))
            self._note = self.session.scalars(statement).one()
        return self._note
    
    @property
    def is_note_dirty(self) -> bool:
        return self._note is None or self._note not in self.session.dirty

    def __init__(self, base: AsyncJobRuntimeContext, session: Session):
        self._extend(base)
        self.session = session


class NotePostprocessor:
    context: NotePostprocessorContext

    @property
    def note_id(self) -> UUID:
        return self.context.note_id
    
    @property
    def note(self) -> NotesNote:
        return self.context.note
    
    @property
    def session(self) -> Session:
        return self.context.session

    def __init__(self, context: NotePostprocessorContext):
        self.context = context

    def should_run(self) -> bool:
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()


class PostprocessHandler(AsyncJobHandler):
    TYPE = "postprocess"

    def select_postprocessor(self, context: NotePostprocessorContext):
        postprocessor_classes = NotePostprocessor.__subclasses__()
        for cls in postprocessor_classes:
            postprocessor = cls(context)
            if postprocessor.should_run():
                return postprocessor

    def run(self):
        with self.context.database.make_session() as session:
            context = NotePostprocessorContext(self.context, session)
            postprocessor = self.select_postprocessor(context)
            if postprocessor is not None:
                assert not context.is_note_dirty, "NotePostprocessor.should_run() shouldn't modify the note"
                return postprocessor.run()
