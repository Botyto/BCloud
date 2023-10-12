import os
import shutil
from typing import BinaryIO, cast

from .base import Address, BlobIO, OpenMode, Blobs


class FsBlobIO(BlobIO):
    _path: str
    _handle: BinaryIO

    def __init__(self, path: str, manager: Blobs, address: Address, mode: OpenMode):
        super().__init__(manager, address, mode)
        self._path = path

    def __enter__(self):
        self._handle = cast(BinaryIO, open(self._path, self.mode))
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._handle.close()
        del self._handle

    def close(self):
        return self._handle.close()

    def flush(self):
        return self._handle.flush()

    def read(self, n: int = -1) -> bytes:
        return self._handle.read(n)

    def seek(self, offset: int, whence: int = 0) -> int:
        return self._handle.seek(offset, whence)

    def tell(self) -> int:
        return self._handle.tell()

    def write(self, data: bytes|bytearray) -> int:
        return self._handle.write(data)


class FsBlobs(Blobs):
    root: str

    def __init__(self, root: str):
        self.root = root

    def _addr_to_path(self, address: Address, create_dirs: bool = True, ensure_exists: bool = False) -> str:
        address_str = str(address)
        if address_str.startswith("/"):
            address_str = address_str[1:]
        path = os.path.join(self.root, address_str)
        if create_dirs:
            dirname = os.path.dirname(path)
            os.makedirs(dirname, exist_ok=True)
        if ensure_exists:
            assert not create_dirs, "Cannot ensure_exists and create_dirs at the same time"
            if not os.path.isfile(path):
                raise FileNotFoundError(path)
        return path

    def exists(self, address: Address):
        path = self._addr_to_path(address, create_dirs=False)
        return os.path.isfile(path)

    def delete(self, address: Address):
        path = self._addr_to_path(address, create_dirs=False)
        if os.path.isfile(path):
            return os.remove(path)
        elif os.path.isdir(path):
            return shutil.rmtree(path)
    
    def open(self, address: Address, mode: OpenMode):
        path = self._addr_to_path(address, create_dirs=mode != OpenMode.READ)
        return FsBlobIO(path, self, address, mode)
    
    def copy(self, src: Address, dst: Address):
        src_path = self._addr_to_path(src, create_dirs=False)
        dst_path = self._addr_to_path(dst, create_dirs=True)
        return shutil.copyfile(src_path, dst_path, follow_symlinks=False)
    
    def rename(self, src: Address, dst: Address):
        src_path = self._addr_to_path(src, create_dirs=False)
        dst_path = self._addr_to_path(dst, create_dirs=True)
        return os.rename(src_path, dst_path)
