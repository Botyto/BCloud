from dataclasses import dataclass
from enum import Enum
import os
from typing import BinaryIO
import uuid


@dataclass
class Address:
    namespace: str
    key: str
    temporary: bool = False

    @classmethod
    def random(cls, namespace: str, key_prefix: str = "", temporary: bool = False):
        return cls(namespace, os.path.join(key_prefix, str(uuid.uuid4())), temporary=temporary)
    
    @classmethod
    def unique(cls, manager: "BlobManager", namespace: str, key_prefix: str = "", temporary: bool = False):
        address = cls.random(namespace, key_prefix, temporary=temporary)
        original_key = address.key
        n = 0
        while manager.exists(address):
            n += 1
            address.key = original_key + f"-{n}"
        return address

    @classmethod
    def join_keys(cls, *keys: str) -> str:
        return os.path.join(*keys)

    def __str__(self):
        return os.path.join(
            "tempdata" if self.temporary else "appdata",
            self.namespace,
            self.key,
        )
    
    def __repr__(self):
        return str(self)


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
        with self.open(address, OpenMode.WRITE) as fh:
            return fh.write(data)

    def delete(self, address: Address):
        raise NotImplementedError()
    
    def open(self, address: Address, mode: OpenMode) -> BlobFile:
        raise NotImplementedError()
    
    def copy(self, src: Address, dst: Address):
        raise NotImplementedError()
    
    def rename(self, src: Address, dst: Address):
        raise NotImplementedError()
