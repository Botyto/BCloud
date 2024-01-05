from typing import List

from .background import NotePostprocessor
from .data import NotesTag


class AutoTagPostprocessor(NotePostprocessor):
    MAX_TAGS = 5

    _precached: bool = False

    def precache(self):
        if self._precached:
            return
        self._precached = True
        if self.note.tags or len(self.note.content) < 10:
            return
        return True

    def should_run(self):
        self.precache()
        return True
    
    def extract_tags(self, text: str) -> List[str]:
        return [w for w in text.split() if len(w) > 3]
    
    def run(self):
        assert self._precached, "precache() should be called before run()"
        tags = self.extract_tags(self.note.content)
        if not tags:
            return
        if len(tags) > self.MAX_TAGS:
            tags = tags[:self.MAX_TAGS]
        self.note.tags = [
            NotesTag(name=tag, note_id=self.note_id, note=self.note)
            for tag in tags
        ]
        self.session.add_all(self.note.tags)
        self.session.commit()
