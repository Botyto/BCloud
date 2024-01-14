from core.miniapp.miniapp import Miniapp, ModuleRegistry

from .albums import AlbumsModule


class PhotosMiniapp(Miniapp):
    def __init__(self):
        super().__init__("photos",
            ModuleRegistry(AlbumsModule),
            dependencies=["profile", "files"],
        )
