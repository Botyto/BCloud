from core.miniapp.miniapp import Miniapp, ModuleRegistry


class PhotosMiniapp(Miniapp):
    def __init__(self):
        super().__init__("photos",
            dependencies=["profile", "files"],
        )
