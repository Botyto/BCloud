import boto3
import botocore.exceptions
from mypy_boto3_s3 import S3Client
import os
import tempfile
from typing import BinaryIO, cast

from .base import Address, Blobs, BlobIO, OpenMode


class S3BlobIO(BlobIO):
    _manager: "S3Blobs"
    key: str
    temp_file: BinaryIO|tempfile._TemporaryFileWrapper

    @property
    def client(self):
        return self._manager.client

    @property
    def bucket(self):
        return self._manager.bucket
    
    @property
    def internal_file(self) -> BinaryIO:
        return cast(BinaryIO, self.temp_file.file)  # type: ignore

    def __init__(self, manager: "S3Blobs", address: Address, mode: OpenMode, key: str):
        super().__init__(manager, address, mode)
        self.key = key

    def __enter__(self):
        mode_str = "w+b" if self._mode != OpenMode.APPEND else "a+b"
        self.temp_file = cast(BinaryIO, tempfile.TemporaryFile(mode_str))
        try:
            self.client.download_fileobj(self.bucket, self.key, self.internal_file)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] not in ("404", "403"):  # type: ignore
                raise
        self.internal_file.seek(0)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.temp_file.closed:
            self.close()
        del self.temp_file

    def close(self):
        if self._mode == OpenMode.WRITE:
            self.temp_file.flush()
            self.temp_file.seek(0)
            self.client.upload_fileobj(self.internal_file, self.bucket, self.key)
        self.temp_file.close()

    def flush(self):
        self.temp_file.flush()
        if self._mode == OpenMode.WRITE:
            pos = self.temp_file.tell()
            self.temp_file.seek(0)
            self.client.upload_fileobj(self.internal_file, self.bucket, self.key)
            self.temp_file.seek(pos)

    def read(self, n: int = -1):
        return self.temp_file.read(n)

    def seek(self, offset: int, whence: int = 0):
        return self.temp_file.seek(offset, whence)

    def tell(self):
        return self.temp_file.tell()

    def write(self, data: bytes|bytearray):
        return self.temp_file.write(data)


class S3Blobs(Blobs):
    bucket: str
    session: boto3.Session
    client: S3Client

    def __init__(self, bucket: str):
        credentials, bucket_name = tuple(bucket.split("@"))
        aws_id, aws_secret = tuple(credentials.split(":"))
        self.bucket = bucket_name
        self.session = boto3.Session(aws_id, aws_secret)
        self.client = self.session.client("s3")

    def __addr_to_key(self, address: Address) -> str:
        path = str(address)
        if path.startswith("/"):
            path = path[1:]
        path = "/".join(part.strip() for part in path.split("/"))
        path = os.path.normpath(path)
        path = path.replace(os.path.sep, "/")
        return path

    def exists(self, address: Address) -> bool:
        key = self.__addr_to_key(address)
        obj = self.client.head_object(Bucket=self.bucket, Key=key)
        metadata = obj["Metadata"]
        return metadata["Status"] in ["active", "inactive"]

    def delete(self, address: Address):
        key = self.__addr_to_key(address)
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def open(self, address: Address, mode: OpenMode) -> S3BlobIO:
        key = self.__addr_to_key(address)
        return S3BlobIO(self, address, mode, key)  # type: ignore

    def copy(self, src: Address, dst: Address):
        src_key = self.__addr_to_key(src)
        dst_key = self.__addr_to_key(dst)
        copy_source = {"Bucket": self.bucket, "Key": src_key}
        self.client.copy_object(Bucket=self.bucket, CopySource=copy_source, Key=dst_key)  # type: ignore

    def rename(self, src: Address, dst: Address):
        src_key = self.__addr_to_key(src)
        dst_key = self.__addr_to_key(dst)
        copy_source = {"Bucket": self.bucket, "Key": src_key}
        self.client.copy_object(Bucket=self.bucket, CopySource=copy_source, Key=dst_key)  # type: ignore
        self.client.delete_object(Bucket=self.bucket, Key=src_key)
