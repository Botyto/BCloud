from dataclasses import dataclass
from enum import Enum
from typing import BinaryIO
import uuid


@dataclass
class Address:
    namespace: str
    key: str
    temporary: bool = False

    @classmethod
    def random(cls, namespace: str, temporary: bool = False):
        return cls(namespace, str(uuid.uuid4()), temporary=temporary)


class OpenMode(Enum):
    READ = "read"
    WRITE = "write"
    APPEND = "append"


class BlobFile(BinaryIO):
    _manager: "BlobManager"
    _address: Address
    _mode: OpenMode

    def __init__(self, manager: "BlobManager", address: Address, mode: OpenMode):
        self._manager = manager
        self._address = address
        self._mode = mode

    def close(self):
        raise NotImplementedError()

    def flush(self):
        raise NotImplementedError()
    
    @property
    def mode(self):
        match self._mode:
            case OpenMode.READ:
                return "rb"
            case OpenMode.WRITE:
                return "wb"
            case OpenMode.APPEND:
                return "ab"
        return "rb"

    def read(self, n: int = -1) -> bytes:
        raise NotImplementedError()

    def seek(self, offset: int, whence: int = 0) -> int:
        raise NotImplementedError()

    def tell(self) -> int:
        raise NotImplementedError()

    def write(self, data: bytes|bytearray) -> int:
        raise NotImplementedError()


class BlobManager:
    def exists(self, address: Address) -> bool:
        raise NotImplementedError()

    def read(self, address: Address) -> bytes:
        with self.open(address, OpenMode.READ) as fh:
            return fh.read()

    def write(self, address: Address, data: bytes|bytearray):
        with self.open(address, OpenMode.READ) as fh:
            return fh.write(data)

    def delete(self, address: Address):
        raise NotImplementedError()
    
    def open(self, address: Address, mode: OpenMode) -> BlobFile:
        raise NotImplementedError()
    
    def copy(self, src: Address, dst: Address):
        raise NotImplementedError()
    
    def rename(self, src: Address, dst: Address):
        raise NotImplementedError()
