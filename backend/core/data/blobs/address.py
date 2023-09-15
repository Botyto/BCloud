from __future__ import annotations
from dataclasses import dataclass
import os
from typing import TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from .base import Blobs

@dataclass
class Address:
    namespace: str
    key: str
    temporary: bool = False

    @classmethod
    def random(cls, namespace: str, key_prefix: str = "", temporary: bool = False):
        return cls(namespace, os.path.join(key_prefix, str(uuid.uuid4())), temporary=temporary)
    
    @classmethod
    def unique(cls, manager: Blobs, namespace: str, key_prefix: str = "", temporary: bool = False):
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