from abc import ABC, abstractmethod
from dataclasses import dataclass
import io
from typing import List, BinaryIO

import mimetypes
mimetypes.guess_type


@dataclass
class ArchiveFile:
    path: str
    mime: str|None = None
    size: int|None = None


@dataclass
class ArchiveFileList:
    files: List[ArchiveFile]


@dataclass
class ArchiveFileContent:
    data: bytes
    mime: str|None = None


class UnknownArchiveError(Exception):
    def __init__(self):
        super().__init__("Unknown archive type")


class ArchivePreview(ABC):
    MULTIFILE: bool

    blob: BinaryIO

    def __init__(self, blob: BinaryIO):
        self.blob = blob

    @abstractmethod
    def _unarchive(self) -> BinaryIO:
        ...

    @abstractmethod
    def _list_files(self) -> List[ArchiveFile]:
        ...
    
    @abstractmethod
    def _read_file(self, path: str) -> ArchiveFileContent:
        ...
    
    @classmethod
    def _open(cls, blob: BinaryIO) -> "ArchivePreview":
        for cls in ArchivePreview.__subclasses__():
            try:
                obj = cls(blob)
                if obj.MULTIFILE:
                   return obj
                else:
                    unarchived_blob = obj._unarchive()
                    return cls._open(unarchived_blob)
            except:
                pass
        raise UnknownArchiveError()
    
    @classmethod
    def list_files(cls, blob: BinaryIO):
        return ArchiveFileList(cls._open(blob)._list_files())
    
    @classmethod
    def read_file(cls, blob: BinaryIO, path: str):
        return cls._open(blob)._read_file(path)


import zipfile
class ZipArchivePreview(ArchivePreview):
    MULTIFILE = True

    def _list_files(self):
        result: List[ArchiveFile] = []
        with zipfile.ZipFile(self.blob) as zf:
            for file in zf.filelist:
                result.append(ArchiveFile(file.filename, size=file.file_size))
        return result
    
    def _read_file(self, path: str):
        with zipfile.ZipFile(self.blob) as zf:
            with zf.open(path) as fh:
                return ArchiveFileContent(fh.read())


import tarfile
class TarArchivePreview(ArchivePreview):
    MULTIFILE = True

    def _list_files(self):
        result: List[ArchiveFile] = []
        with tarfile.open(fileobj=self.blob) as tf:
            for file in tf.getmembers():
                result.append(ArchiveFile(file.name, size=file.size))
        return result
    
    def _read_file(self, path: str):
        with tarfile.open(fileobj=self.blob) as tf:
            fh = tf.extractfile(path)
            if fh is None:
                raise FileNotFoundError(path)
            with fh:
                return ArchiveFileContent(fh.read())


import gzip
class GZipArchivePreview(ArchivePreview):
    MULTIFILE = False

    def _unarchive(self):
        with gzip.open(self.blob) as fh:
            return io.BytesIO(fh.read())


import bz2
class Bz2ArchivePreview(ArchivePreview):
    MULTIFILE = False
    
    def _unarchive(self):
        with bz2.open(self.blob) as fh:
            return io.BytesIO(fh.read())


import lzma
class LzmaArchivePreview(ArchivePreview):
    MULTIFILE = False
    
    def _unarchive(self):
        with lzma.open(self.blob) as fh:
            return io.BytesIO(fh.read())
