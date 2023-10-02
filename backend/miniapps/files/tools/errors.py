class FileError(Exception):
    def __init__(self, msg: str, path: str):
        super().__init__(f"{msg}: {path}")


class DirectoryNotFound(FileError):
    def __init__(self, path: str):
        super().__init__("Directory not found", path)


class FileAlreadyExists(FileError):
    def __init__(self, path: str):
        super().__init__("File already exists", path)


class StorageNotSpecified(FileError):
    def __init__(self, path: str):
        super().__init__("Storage not specified", path)
