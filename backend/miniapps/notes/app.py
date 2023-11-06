from core.miniapp.miniapp import Miniapp, ModuleRegistry

from .collections import CollectionsModule


class NotesMiniapp(Miniapp):
    def __init__(self):
        super().__init__("files",
            ModuleRegistry(CollectionsModule),
            dependencies=["profile", "files"],
        )
