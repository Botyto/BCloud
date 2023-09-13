from dataclasses import dataclass

from .manager import BlobManager

@dataclass
class BlobsSettings:
    manager: BlobManager
