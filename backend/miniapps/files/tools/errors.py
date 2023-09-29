class FileError(Exception):
    pass


class DirectoryNotFound(FileError):
    pass


class FileAlreadyExists(FileError):
    pass


class StorageNotSpecified(FileError):
    pass
