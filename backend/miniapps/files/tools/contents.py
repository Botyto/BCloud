from dataclasses import dataclass
from uuid import UUID

from . import fspath
from ..data import FileMetadata

from core.data.sql.columns import ensure_str_fit
from core.data.blobs.address import Address
from core.data.blobs.base import Blobs, OpenMode


@dataclass
class Namespace:
    name: str
    update_orm: bool

NAMESPACE_CONTENT = Namespace("content", True)


class FileContents:
    blobs: Blobs
    namespace: Namespace
    scramble: bool

    def __init__(self, blobs: Blobs, namespace: Namespace = NAMESPACE_CONTENT, scramble: bool = False):
        self.blobs = blobs
        self.namespace = namespace
        self.scramble = scramble

    def address(self, file: FileMetadata|str, temporary: bool = False):
        if isinstance(file, FileMetadata):
            file = file.abspath
        storage_id, path = fspath.strip_storage(file)
        if path.startswith("/root"):
            path = path[5:]
        if not isinstance(storage_id, UUID):
            raise ValueError("File path must be absolute and have UUID as storage ID")
        if self.scramble:
            prefix = Address.join_keys(str(storage_id), self.namespace.name)
            return Address.scrambled("files", prefix, path, temporary)
        key = Address.join_keys(str(storage_id), self.namespace.name, path)
        return Address("files", key, temporary)
    
    def exists(self, file: FileMetadata):
        return self.blobs.exists(self.address(file))

    def read(self, file: FileMetadata):
        result = self.blobs.read(self.address(file))
        if self.namespace.update_orm:
            file.accessed()
        return result
    
    def write(self, file: FileMetadata, content: bytes|None, mime_type: str|None = None):
        if content is None:
            self.blobs.delete(self.address(file))
            file.size = None
            file.mime_type = None
        else:
            self.blobs.write(self.address(file), content)
            file.size = len(content)
            if mime_type is not None:
                ensure_str_fit("MIME-Type", mime_type, FileMetadata.mime_type)
                file.mime_type = mime_type
        if self.namespace.update_orm:
                file.modified()
    
    def delete(self, file: FileMetadata):
        self.blobs.delete(self.address(file))
        if self.namespace.update_orm:
            file.modified()

    def open(self, file: FileMetadata, mode: OpenMode):
        return self.blobs.open(self.address(file), mode)

    def copy(self, src: FileMetadata, dst: FileMetadata):
        self.blobs.copy(self.address(src), self.address(dst))
        if self.namespace.update_orm:
            dst.size = src.size
            dst.modified()

    def rename(self, src: FileMetadata, dst: str):
        self.blobs.rename(self.address(src), self.address(dst))
        if self.namespace.update_orm:
            src.modified()
