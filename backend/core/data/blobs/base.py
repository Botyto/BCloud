from abc import ABC, abstractmethod
from enum import Enum
from typing import BinaryIO

from .address import Address

class OpenMode(Enum):
    READ = "read"
    WRITE = "write"
    APPEND = "append"


class BlobIO(ABC, BinaryIO):
    _manager: "Blobs"
    _address: Address
    _mode: OpenMode

    def __init__(self, manager: "Blobs", address: Address, mode: OpenMode):
        self._manager = manager
        self._address = address
        self._mode = mode

    @abstractmethod
    def close(self):
        ...

    @abstractmethod
    def flush(self):
        ...
    
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

    @abstractmethod
    def read(self, n: int = -1) -> bytes:
        ...

    @abstractmethod
    def seek(self, offset: int, whence: int = 0) -> int:
        ...

    @abstractmethod
    def tell(self) -> int:
        ...

    @abstractmethod
    def write(self, data: bytes|bytearray) -> int:
        ...


class Blobs(ABC):
    @abstractmethod
    def exists(self, address: Address) -> bool:
        ...

    def read(self, address: Address) -> bytes:
        with self.open(address, OpenMode.READ) as fh:
            return fh.read()

    def write(self, address: Address, data: bytes|bytearray):
        with self.open(address, OpenMode.WRITE) as fh:
            return fh.write(data)

    @abstractmethod
    def delete(self, address: Address):
        ...
    
    @abstractmethod
    def open(self, address: Address, mode: OpenMode) -> BlobIO:
        ...
    
    @abstractmethod
    def copy(self, src: Address, dst: Address):
        ...
    
    @abstractmethod
    def rename(self, src: Address, dst: Address):
        ...
