from dataclasses import dataclass

from .base import Blobs
from .fs import FsBlobs
from .sql import SqlBlobs


@dataclass
class BlobSettings:
    fs_root: str|None = None
    sql_conn_str: str|None = None

    def build_manager(self) -> Blobs:
        if self.fs_root is not None:
            return FsBlobs(self.fs_root)
        elif self.sql_conn_str is not None:
            return SqlBlobs(self.sql_conn_str)
        raise ValueError("No blobs configured")
