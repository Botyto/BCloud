from dataclasses import dataclass

from .manager import BlobManager
from .fs import FsBlobManager


@dataclass
class BlobSettings:
    fs_root: str

    def build_manager(self) -> BlobManager:
        return FsBlobManager(self.fs_root)
