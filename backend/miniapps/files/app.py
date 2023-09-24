from core.miniapp.miniapp import Miniapp

from .storage import StorageModule


class FilesMiniapp(Miniapp):
    def __init__(self):
        super().__init__("files", module_types=[
            StorageModule,
        ])
