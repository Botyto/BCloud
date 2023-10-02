const sep = "/";
const storageSep = ":";
const currentDir = ".";
const parentDir = "..";
const uuidLength = 36;
const uuidRegex = /^[0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i;

function isValid(path: string) {
    if (!path || path === "") {
        return false;
    }
    const [storage_id, file_path] = stripStorage(path);
    if (storage_id !== null) {
        return file_path.startsWith(sep);
    }
    return true;
}

function hasStorage(path: string) {
    const colon_idx = path.indexOf(":");
    if (colon_idx !== uuidLength) {
        return false;
    }
    return uuidRegex.exec(path.slice(0, colon_idx)) !== null;
}

function stripStorage(path: string): [string|null, string] {
    if (hasStorage(path)) {
        const storage_id = path.slice(0, uuidLength);
        const file_path = path.slice(uuidLength + 1);
        return [storage_id, file_path];
    }
    return [null, path];
}

function isAbs(path: string) {
    if (hasStorage(path)) {
        return path[uuidLength] == storageSep;
    }
    return path.startsWith(sep);
}

function join(storage_id: string|null, parts: string[]) {
    if (!parts || parts.length === 0) {
        if (storage_id !== null) {
            return `${storage_id}${storageSep}${sep}`;
        }
        return sep;
    }
    if (storage_id !== null) {
        if (!parts[0].startsWith(sep)) {
            parts = [sep, ...parts];
        }
        return `${storage_id}${storageSep}${parts.join(sep)}`;
    }
    return parts.join(sep);
}

function normPath(path: string) {
    var [storage_id, parts] = getParts(path);
    var i = 0;
    while (i < parts.length) {
        if (parts[i] == currentDir) {
            parts = parts.splice(i, 1);
        } else if (parts[i] == parentDir) {
            if (i === 0) {
                throw "Expected absolute path";
            }
            parts = parts.splice(i - 1, 2);
            i -= 1;
        } else {
            i += 1;
        }
    }
    return join(storage_id, parts)
}

function getParts(path: string): [string|null, string[]] {
    const [storage_id, file_path] = stripStorage(path);
    const parts = path.split(sep).filter((part) => part !== "");;
    return [storage_id, parts];
}

function dirName(path: string) {
    const sep_idx = path.lastIndexOf(sep);
    if (sep_idx === -1) {
        return path;
    }
    return path.slice(0, sep_idx);
}

function baseName(path: string) {
    const sep_idx = path.lastIndexOf(sep);
    if (sep_idx === -1) {
        const [_, file_path] = stripStorage(path);
        return file_path;
    }
    return path.slice(sep_idx + 1);
}

function ext(path: string) {
    const period_idx = path.lastIndexOf(".");
    if (period_idx === -1) {
        return "";
    }
    return path.slice(period_idx);
}
