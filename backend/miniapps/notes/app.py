from core.miniapp.miniapp import AsyncjobRegistry, ClassRegistry, Miniapp, ModuleRegistry

from .collections import CollectionsModule
from .notes import NotesModule
from .attachments import NoteAttachmentsModule
from .background import PostprocessHandler
from .cache import HtmlCachePostprocessor
from .tags import AutoTagPostprocessor


class NotesMiniapp(Miniapp):
    def __init__(self):
        super().__init__("notes",
            ModuleRegistry(CollectionsModule),
            ModuleRegistry(NotesModule),
            ModuleRegistry(NoteAttachmentsModule),
            AsyncjobRegistry(PostprocessHandler),
            ClassRegistry(HtmlCachePostprocessor),
            ClassRegistry(AutoTagPostprocessor),
            dependencies=["profile", "files"],
        )
