import mimetypes

from core.miniapp.miniapp import Miniapp, ModuleRegistry, SqlEventRegistry, ClassRegistry, MiniappContext

from .storage import StorageModule
from .files import FilesModule, DeleteFileEvent
from .contents import ContentsModule
from .previews.module import PreviewModule
from .importing import GoogleDriveImporter
from .wopi import WopiModule, WopiMapping


class FilesMiniapp(Miniapp):
    wopi: WopiMapping

    def __init__(self):
        super().__init__("files",
            ModuleRegistry(StorageModule),
            ModuleRegistry(FilesModule),
            ModuleRegistry(ContentsModule),
            ModuleRegistry(PreviewModule),
            SqlEventRegistry(DeleteFileEvent),
            ClassRegistry(GoogleDriveImporter),
            dependencies=["profile"],
        )

    def start(self, context: MiniappContext):
        mimetypes.add_type("text/markdown", ".md")
        self.wopi = WopiMapping()
        return super().start(context)
