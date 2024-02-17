from dataclasses import dataclass
import os
from typing import cast, Optional

from core.env import Environment

from .base import Blobs
from .fs import FsBlobs
from .sql import SqlBlobs
from .s3 import S3Blobs


@dataclass
class BlobSettings:
    fs_root: str|None = None
    sql_conn_str: str|None = None
    s3_bucket: str|None = None

    def build(self) -> Blobs:
        if self.fs_root is not None:
            return FsBlobs(self.fs_root)
        elif self.sql_conn_str is not None:
            return SqlBlobs(self.sql_conn_str)
        elif self.s3_bucket is not None:
            return S3Blobs(self.s3_bucket)
        raise ValueError("No blobs configured")
    
    @classmethod
    def from_env(cls, env: Environment):
        fs_root = cast(Optional[str], env.get("BLOB_FS_ROOT"))
        if fs_root is not None:
            return cls(fs_root=os.path.abspath(fs_root))
        sql_conn_str = cast(Optional[str], env.get("BLOB_SQL"))
        if sql_conn_str is not None:
            return cls(sql_conn_str=sql_conn_str)
        s3_bucket = cast(Optional[str], env.get("BLOB_S3"))
        if s3_bucket is not None:
            return cls(s3_bucket=s3_bucket)
        return cls()
