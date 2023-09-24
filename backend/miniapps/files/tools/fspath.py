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
UUID_LENGTH = 36


class AbsolutePathExpected(Exception):
    def __init__(self, path: str):
        super().__init__(f"Absolute path expected, but got '{path}'")

def isvalid(path: str):
    if not path:
        return False
    storage_id, path = strip_storage(path)
    if storage_id is not None:
        return path.startswith(SEP)
    return True

def hasstorage(path: str):
    colon_idx = path.find(":")
    if colon_idx != UUID_LENGTH:
        return False
    try:
        UUID(path[:colon_idx])
    except ValueError:
        return False
    return True

def strip_storage(path: str):
    if hasstorage(path):
        storage_id = path[:UUID_LENGTH]
        path = path[UUID_LENGTH + 1:]
        return UUID(storage_id), path
    return None, path

def isabs(path: str):
    if hasstorage(path):
        return path[UUID_LENGTH] == STORAGE_SEP
    return path.startswith(SEP)

def expect_abs(path: str):
    if not isabs(path):
        raise AbsolutePathExpected(path)

def join(storage_id: UUID|None, *parts: str):
    if not parts:
        if storage_id is not None:
            return f"{storage_id}{STORAGE_SEP}{SEP}"
        return SEP
    if storage_id is not None:
        if not parts[0].startswith(SEP):
            parts = (SEP,) + parts
        return f"{storage_id}{STORAGE_SEP}{SEP.join(parts)}"
    return SEP.join(parts)

def normapth(path: str):
    storage_id, parts = get_parts(path)
    i = 0
    while i < len(parts):
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
    storage_id, path = strip_storage(path)
    parts = [part for part in path.split(SEP) if part]
    return storage_id, parts

def dirname(path: str):
    sep_idx = path.rfind(SEP)
    if sep_idx == -1:
        return path
    return path[:sep_idx]

def basename(path: str):
    sep_idx = path.rfind(SEP)
    if sep_idx == -1:
        _, path = strip_storage(path)
        return path
    return path[sep_idx + 1:]

def ext(path: str):
    period_idx = path.rfind(".")
    if period_idx == -1:
        return ""
    return path[period_idx:]
