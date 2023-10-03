import React from 'react';
import { Link, useParams, generatePath } from 'react-router-dom';
import Loading from '../../components/Loading';
import fspath from './fspath';
import { useFilesListQuery, useFilesMakedirsMutation, useFilesMakefileMutation } from './filesApi';
import MimeTypeIcon from './MimeTypeIcon';

function pathToUrl(route: string, path: string) {
    var [storageId, filePath] = fspath.stripStorage(path);
    if (filePath.startsWith(fspath.sep)) {
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
    return fspath.join(storageId, [filePath]);
}

interface BreadcrumbsPiece {
    name: string;
    url: string;
    current: boolean;
}

const BROWSER_ROUTE = "/files/:storageId/*";
function makeBreadcrumbs(storageName: string, storageId: string, parts: string[]) {
    const result: BreadcrumbsPiece[] = [];
    for (var i = 0; i < parts.length + 1; i++) {
        const subparts = parts.slice(0, i);
        var part = (i === 0) ? storageName : parts[i - 1];
        if (part.startsWith(fspath.sep)) {
            part = part.slice(1);
        }
        result.push({
            name: part,
            url: pathToUrl(BROWSER_ROUTE, fspath.join(storageId, subparts)),
            current: (i === parts.length),
        });
    }
    return result;
}

interface BreacumbsProps {
    pieces: BreadcrumbsPiece[];
}

function Breadcrumbs(props: BreacumbsProps) {
    return <span>
        {
            props.pieces.map((piece, i) => {
                return (piece.current) ? (
                    <span key={i}>
                        {piece.name}
                        {(i < props.pieces.length - 1) ? " / " : ""}
                    </span>
                ) : (
                    <span key={i}>
                        <Link to={piece.url}>{piece.name}</Link>
                        {(i < props.pieces.length - 1) ? " / " : ""}
                    </span>
                );
            })
        }
    </span>;
}

interface ContentsProps {
    path: string;
    file: any;
}

function DirectoryContents(props: ContentsProps) {
    return (props.file.children.length === 0) ? (
        <span>Empty...</span>
    ) : (props.file.children.map((file: any) => {
            return <li key={file.id}>
                <MimeTypeIcon type={file.type} mimeType={file.mimeType}/>
                <Link to={pathToUrl(BROWSER_ROUTE, fspath.join(null, [props.path, file.name]))}>
                    {file.name}
                </Link>
            </li>;
        })
    )
}

function FileContents(props: ContentsProps) {
    const downloadUrl = pathToUrl("/api/files/download/:storageId/*", props.path)
    return <>
        <a href={downloadUrl} target='_blank'>Download</a>
        <span>File content...</span>
    </>;
}

function LinkContents(props: ContentsProps) {
    return <span>Follow link...</span>
}

export default function Browser() {
    const params = useParams();
    const storageId = params.storageId || "";
    const filePath = params["*"] || "";
    const [_, parts] = fspath.getParts(filePath);
    const fullPath = fspath.join(storageId, parts);
    const filesListVars = useFilesListQuery(fullPath);
    const breadcrumbs = makeBreadcrumbs(storageId, storageId, parts);

    const [makefile, makefileVars] = useFilesMakefileMutation();
    const [makedirs, makedirsVars] = useFilesMakedirsMutation();

    function onNewFile(e: React.MouseEvent<HTMLButtonElement, MouseEvent>) {
        e.preventDefault();
        const name = prompt("File name", "newfile.txt");
        if (!name) { return; }
        const newPath = fspath.join(storageId, [...parts, name])
        makefile({
            variables: {
                path: newPath,
                mimeType: "text/plain",
            },
            onError: (e) => {
                alert(e.message);
            },
        });
    }

    function onNewDir(e: React.MouseEvent<HTMLButtonElement, MouseEvent>) {
        e.preventDefault();
        const name = prompt("Directory name", "newdir");
        if (!name) { return; }
        const newPath = fspath.join(storageId, [...parts, name])
        makedirs({
            variables: {
                path: newPath,
            },
            onError: (e) => {
                alert(e.message);
            },
        });
    }

    return <>
        <div>Browser (<Link to="/files">storages</Link>)</div>
        <div>Path: <Breadcrumbs pieces={breadcrumbs}/></div>
        <div>
            <ol>
                {
                    (filesListVars.loading) ? (
                        <Loading/>
                    ) : (filesListVars.error) ? (
                            <span style={{ color: "red" }}>Error: {filesListVars.error.message}</span>
                    ) : (filesListVars.data.filesFilesByPath.type === "DIRECTORY") ? (
                        <DirectoryContents file={filesListVars.data.filesFilesByPath} path={fullPath}/>
                    ) : (filesListVars.data.filesFilesByPath.type === "FILE") ? (
                        <FileContents file={filesListVars.data.filesFilesByPath} path={fullPath}/>
                    ) : (filesListVars.data.filesFilesByPath.type === "LINK") ? (
                        <LinkContents file={filesListVars.data.filesFilesByPath} path={fullPath}/>
                    ) : (
                        <span>Unknown file type {filesListVars.data.filesFilesByPath.type}</span>
                    )
                }
            </ol>
        </div>
        <div>
            <button onClick={onNewFile}>New file</button>
            <button onClick={onNewDir}>New directory</button>
        </div>
    </>;
}
