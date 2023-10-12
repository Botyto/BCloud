from core.miniapp.miniapp import Miniapp, ModuleRegistry

from .storage import StorageModule
from .files import FilesModule
from .contents import ContentsModule
from .importing import GoogleDriveImporter


class FilesMiniapp(Miniapp):
    def __init__(self):
        super().__init__("files",
            ModuleRegistry(StorageModule),
            ModuleRegistry(FilesModule),
            ModuleRegistry(ContentsModule),
            dependencies=["profile"],
        )
