import { generatePath } from 'react-router-dom';

const sep = "/";
const storageSep = ":";
const currentDir = ".";
const parentDir = "..";

function isValid(path: string) {
    if (path === "") {
        return false;
    }
    const [storageId, filePath] = stripStorage(path);
    if (storageId !== null) {
        return filePath.startsWith(sep);
    }
    return true;
}

function hasStorage(path: string) {
    return path.indexOf(":") !== -1;
}

function stripStorage(path: string): [string|null, string] {
    if (hasStorage(path)) {
        const colonidx = path.indexOf(":");
        const storageId = path.slice(0, colonidx);
        const filePath = path.slice(colonidx + 1);
        return [storageId, filePath];
    }
    return [null, path];
}

function isAbs(path: string) {
    const colonidx = path.indexOf(":");
    return colonidx !== -1 || path.startsWith(sep);
}

function join(storageId: string|null, parts: string[]) {
    if (parts.length === 0) {
        if (storageId !== null) {
            return `${storageId}${storageSep}${sep}`;
        }
        return sep;
    }
    parts = parts.map((p) => p.endsWith(sep) ? p.slice(0, p.length - 1) : p);
    if (storageId !== null) {
        if (!parts[0].startsWith(sep)) {
            parts = [sep + parts[0], ...parts.slice(1)];
        }
        return `${storageId}${storageSep}${parts.join(sep)}`;
    }
    return parts.join(sep);
}

function normPath(path: string) {
    var [storageId, parts] = getParts(path);
    var i = 0;
    while (i < parts.length) {
        parts[i] = parts[i].trim();
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
    return join(storageId, parts)
}

function getParts(path: string): [string|null, string[]] {
    const [storageId, filePath] = stripStorage(path);
    const parts = filePath.split(sep).filter((part) => part !== "");;
    return [storageId, parts];
}

function dirName(path: string) {
    const sepIdx = path.lastIndexOf(sep, path.length - 2);
    if (sepIdx === -1) {
        return path;
    }
    return path.slice(0, sepIdx + 1);
}

function baseName(path: string) {
    const sepIdx = path.lastIndexOf(sep);
    if (sepIdx === -1) {
        const [_, filePath] = stripStorage(path);
        return filePath;
    }
    return path.slice(sepIdx + 1);
}

function ext(path: string) {
    const periodIdx = path.lastIndexOf(".");
    if (periodIdx === -1) {
        return "";
    }
    return path.slice(periodIdx);
}

// Path <-> URL

function pathToUrl(route: string, path: string) {
    var [storageId, filePath] = stripStorage(path);
    if (filePath.startsWith(sep)) {
        filePath = filePath.slice(1);
    }
    return generatePath(route, {
        storageId: storageId,
        "*": filePath,
    });
}

function urlToPath(route: string, url: string) {
    const routeStorageIdx = route.indexOf(":storageId");
    if (route.slice(routeStorageIdx) !== ":storageId/*") {
        throw `File route '${route}' doesn't end in ':storageId/*'`;
    }
    const pathInUrl = url.slice(routeStorageIdx + ":storageId".length + 1);
    const slashIdx = pathInUrl.indexOf("/");
    const storageId = pathInUrl.slice(0, slashIdx);
    const filePath = pathInUrl.slice(slashIdx);
    return join(storageId, [filePath]);
}

export default {
    sep,
    storageSep,
    isValid,
    hasStorage,
    stripStorage,
    isAbs,
    join,
    normPath,
    getParts,
    dirName,
    baseName,
    ext,
    pathToUrl,
    urlToPath,
};
