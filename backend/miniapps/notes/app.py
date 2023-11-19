from core.miniapp.miniapp import Miniapp, ModuleRegistry

from .collections import CollectionsModule
from .notes import NotesModule


class NotesMiniapp(Miniapp):
    def __init__(self):
        super().__init__("files",
            ModuleRegistry(CollectionsModule),
            ModuleRegistry(NotesModule),
            dependencies=["profile", "files"],
        )