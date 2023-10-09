from dataclasses import dataclass
from typing import Callable, Set

from googleapiclient.discovery import Resource


@dataclass
class GoogleImporter:
    service: str
    scopes: Set[str]
    callback: Callable[[Resource], None]
