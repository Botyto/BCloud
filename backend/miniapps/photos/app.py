from core.miniapp.miniapp import Miniapp, ModuleRegistry

from .albums import AlbumsModule
from .assets import AssetsModule
from .contents import ContentsModule

class PhotosMiniapp(Miniapp):
    def __init__(self):
        super().__init__("photos",
            ModuleRegistry(AlbumsModule),
            ModuleRegistry(AssetsModule),
            ModuleRegistry(ContentsModule),
            dependencies=["profile", "files"],
        )
