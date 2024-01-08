from uuid import UUID

from core.api.modules.gql import GqlMiniappModule, mutation

from .data import NotesNote, NotesFileKind, NotesFile

from .tools.files import NoteFileManager


class NoteAttachmentsModule(GqlMiniappModule):
    _files: NoteFileManager|None = None

    @property
    def files(self):
        if self._files is None:
            self._files = NoteFileManager(None, self.context.user_id, self.context, self.session)
        return self._files

    @mutation()
    def add_attachment(self, note_id: UUID, kind: NotesFileKind, mime_type: str) -> NotesFile:
        return self.files.default_write(note_id, None, mime_type, kind)

    @mutation()
    def remove_attachment(self, note_id: UUID, attachment_id: UUID) -> NotesNote|None:
        note_file = self.files.delete(attachment_id)
        if note_file is not None:
            return note_file.note
