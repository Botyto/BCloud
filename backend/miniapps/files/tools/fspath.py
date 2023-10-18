from typing import Tuple
from uuid import UUID

# Valid formats:
# storage + abs path: `storage_id:/path/to/file`
# abs path: `/path/to/file`
# rel path: `path/to/file`
# all paths may end in `/`
SEP = "/"
STORAGE_SEP = ":"
CURRENT_DIR = "."
PARENT_DIR = ".."


class AbsolutePathExpected(Exception):
    def __init__(self, path: str):
        super().__init__(f"Absolute path expected, but got '{path}'")

def isvalid(path: str):
    """Returns True if the path is valid"""
    if not path:
        return False
    storage_id, path = strip_storage(path)
    if storage_id is not None:
        return path.startswith(SEP)
    return True

def hasstorage(path: str):
    """Returns True if the path has a storage ID"""
    return path.find(":") != -1

def strip_storage(path: str) -> Tuple[UUID|str|None, str]:
    """Returns the storage ID and the path without the storage ID"""
    if hasstorage(path):
        colon_idx = path.find(":")
        storage_id = path[:colon_idx]
        path = path[colon_idx + 1:]
        try:
            return UUID(storage_id), path
        except ValueError:
            return storage_id, path
    return None, path

def isabs(path: str):
    """Returns True if the path is absolute"""
    return hasstorage(path) or path.startswith(SEP)

def expect_abs(path: str):
    """Raises an exception if the path is not absolute"""
    if not isabs(path):
        raise AbsolutePathExpected(path)

def join(storage_id: UUID|str|None, *parts: str):
    """Join two or more path components, inserting '/' as needed"""
    if not parts:
        if storage_id is not None:
            return f"{storage_id}{STORAGE_SEP}{SEP}"
        return SEP
    parts = tuple(part.removesuffix(SEP) for part in parts)
    if storage_id is not None:
        if not parts[0].startswith(SEP):
            parts = (SEP + parts[0], *parts[1:])
        return f"{storage_id}{STORAGE_SEP}{SEP.join(parts)}"
    return SEP.join(parts)

def normpath(path: str):
    """Normalize a pathname by collapsing redundant separators and up-level references"""
    storage_id, parts = get_parts(path)
    i = 0
    while i < len(parts):
        parts[i] = parts[i].strip()
        if parts[i] == CURRENT_DIR:
            del parts[i]
        elif parts[i] == PARENT_DIR:
            if i == 0:
                raise AbsolutePathExpected(path)
            del parts[i]
            del parts[i - 1]
            i -= 1
        else:
            i += 1
    return join(storage_id, *parts)

def get_parts(path: str):
    """Returns the storage ID and a list of the path components"""
    storage_id, path = strip_storage(path)
    parts = [part.strip() for part in path.split(SEP) if part]
    return storage_id, parts

def dirname(path: str):
    """Returns the same path, but without the last component"""
    sep_idx = path.rfind(SEP)
    if sep_idx == -1 or sep_idx == len(path) - 1:
        return path
    return path[:sep_idx + 1].strip()

def basename(path: str):
    """Returns the final component of a pathname"""
    sep_idx = path.rfind(SEP)
    if sep_idx == -1:
        _, path = strip_storage(path)
        return path
    return path[sep_idx + 1:].strip()

def ext(path: str):
    """Returns the extension of the path (from the last '.' to end of the string)"""
    period_idx = path.rfind(".")
    if period_idx == -1:
        return ""
    return path[period_idx:].strip()
