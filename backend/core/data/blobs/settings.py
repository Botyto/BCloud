from dataclasses import dataclass

from .manager import Blobs
from .fs import FsBlobs


@dataclass
class BlobSettings:
    fs_root: str

    def build_manager(self) -> Blobs:
        return FsBlobs(self.fs_root)
