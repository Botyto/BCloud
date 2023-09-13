from typing import BinaryIO, cast

from .manager import Address, BlobFile, OpenMode, BlobManager


class FsBlobFile(BlobFile):
    _path: str
    _handle: BinaryIO

    def __init__(self, path: str, manager: BlobManager, address: Address, mode: OpenMode):
        super().__init__(manager, address, mode)
        self._path = path

    def __enter__(self):
        self._handle = cast(BinaryIO, open(self._path, self.mode))
        return self

    def __exit__(self):
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
