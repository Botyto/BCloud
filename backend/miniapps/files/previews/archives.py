from dataclasses import dataclass
import io
from typing import List, BinaryIO

import zipfile
import gzip
import tarfile
import bz2
import lzma


@dataclass
class ArchiveFile:
    path: str
    mime: str|None = None


@dataclass
class ArchivePreview:
    files: List[ArchiveFile]


class ArchivePreviews:
    @staticmethod
    def __read_zip(blob: BinaryIO):
        result: List[ArchiveFile] = []
        with zipfile.ZipFile(blob) as zf:
            for file in zf.filelist:
                result.append(ArchiveFile(file.filename))
        return ArchivePreview(result)
    
    @staticmethod
    def __read_tar(blob: BinaryIO):
        result: List[ArchiveFile] = []
        with tarfile.open(fileobj=blob) as tf:
            for file in tf.getmembers():
                result.append(ArchiveFile(file.name))
        return ArchivePreview(result)
    
    @staticmethod
    def __read_gzip(blob: BinaryIO):
        with gzip.open(blob) as fh:
            bytes_io = io.BytesIO(fh.read())
            return ArchivePreviews._archive_preview(bytes_io)
    
    @staticmethod
    def __read_bz2(blob: BinaryIO):
        with bz2.open(blob) as fh:
            bytes_io = io.BytesIO(fh.read())
            return ArchivePreviews._archive_preview(bytes_io)
    
    @staticmethod
    def __read_lzma(blob: BinaryIO):
        with lzma.open(blob) as fh:
            bytes_io = io.BytesIO(fh.read())
            return ArchivePreviews._archive_preview(bytes_io)
    
    PREVIEW_METHODS = [
        __read_zip,
        __read_gzip,
        __read_tar,
        __read_bz2,
        __read_lzma,
    ]

    @classmethod
    def _archive_preview(cls, blob: BinaryIO):
        for method in cls.PREVIEW_METHODS:
            try:
                return method(blob)
            except:
                pass
        raise ValueError("Unsupported archive format")
