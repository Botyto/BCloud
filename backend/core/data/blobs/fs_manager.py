import os
import shutil

from .fs_file import FsBlobFile
from .manager import Address, BlobFile, OpenMode, BlobManager


class FsBlobManager(BlobManager):
    root: str

    def __init__(self, root: str):
        self.root = root

    def _addr_to_path(self, address: Address, create_dirs: bool = True, ensure_exists: bool = False) -> str:
        result = self.root
        if address.temporary:
            result = os.path.join(result, 'tempdata')
        else:
            result = os.path.join(result, 'appdata')
        result = os.path.join(result, address.namespace, address.key + ".blob")
        if create_dirs:
            dirname = os.path.dirname(result)
            os.makedirs(dirname, exist_ok=True)
        if ensure_exists:
            assert not create_dirs, "Cannot ensure_exists and create_dirs at the same time"
            if not os.path.isfile(result):
                raise FileNotFoundError(result)
        return result

    def exists(self, address: Address) -> bool:
        path = self._addr_to_path(address, create_dirs=False)
        return os.path.isfile(path)

    def read(self, address: Address) -> bytes:
        path = self._addr_to_path(address)
        return open(path, "rb").read()

    def write(self, address: Address, data: bytes):
        path = self._addr_to_path(address)
        return open(path, "wb").write(data)

    def delete(self, address: Address):
        path = self._addr_to_path(address, create_dirs=False)
        if os.path.isfile(path):
            return os.remove(path)
        
    def open(self, address: Address, mode: OpenMode) -> BlobFile:
        path = self._addr_to_path(address, create_dirs=False)
        return FsBlobFile(path, self, address, mode)
        
    def copy(self, src: Address, dst: Address):
        src_path = self._addr_to_path(src, create_dirs=False)
        dst_path = self._addr_to_path(dst, create_dirs=True)
        shutil.copyfile(src_path, dst_path, follow_symlinks=False)
    
    def rename(self, src: Address, dst: Address):
        src_path = self._addr_to_path(src, create_dirs=False)
        dst_path = self._addr_to_path(dst, create_dirs=True)
        os.rename(src_path, dst_path)
