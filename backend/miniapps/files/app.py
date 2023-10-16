from core.miniapp.miniapp import Miniapp, ModuleRegistry, SqlEventRegistry

from .storage import StorageModule
from .files import FilesModule, DeleteFileEvent
from .contents import ContentsModule
from .previews.module import PreviewModule
from .importing import GoogleDriveImporter


class FilesMiniapp(Miniapp):
    def __init__(self):
        super().__init__("files",
            ModuleRegistry(StorageModule),
            ModuleRegistry(FilesModule),
            ModuleRegistry(ContentsModule),
            ModuleRegistry(PreviewModule),
            SqlEventRegistry(DeleteFileEvent),
            dependencies=["profile"],
        )
