import React from 'react';
import { Link, useParams, generatePath } from 'react-router-dom';
import Loading from '../../components/Loading';
import fspath from './fspath';
import { useFilesListQuery, useFilesMakedirsMutation, useFilesMakefileMutation } from './filesApi';
import MimeTypeIcon from './MimeTypeIcon';

function generateChildPath(storageId: string, parts: string[], file: any|null) {
    var filePath = file ? fspath.join(null, [...parts, file.name]) : fspath.join(null, parts);
    if (filePath.startsWith(fspath.sep)) {
        filePath = filePath.slice(1);
    }
    return generatePath("/files/:storageId/*", {
        storageId: storageId,
        "*": filePath,
    });
}

interface BreadcrumbsPiece {
    name: string;
    url: string;
    current: boolean;
}

function makeBreadcrumbs(storageName: string, storageId: string, parts: string[]) {
    if (parts.length > 0 && parts[0].startsWith(fspath.sep)) {
        parts = [parts[0].slice(1), ...parts.slice(1)];
    }
    const result: BreadcrumbsPiece[] = [];
    result.push({
        name: storageName,
        url: generateChildPath(storageId, [], null),
        current: parts.length === 0,
    });
    let path = "";
    for (const part of parts) {
        const subpath = fspath.join(null, [path, part]);
        path = subpath;
        result.push({
            name: part,
            url: generateChildPath(storageId, [subpath], null),
            current: part === parts[parts.length - 1],
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
    file: any;
    storageId: string;
    parts: string[];
}

function DirectoryContents(props: ContentsProps) {
    return (props.file.children.length === 0) ? (
        <span>Empty...</span>
    ) : (props.file.children.map((file: any) => {
            return <li key={file.id}>
                <MimeTypeIcon type={file.type} mimeType={file.mimeType}/>
                <Link to={generateChildPath(props.storageId, props.parts, file)}>
                    {file.name}
                </Link>
            </li>;
        })
    )
}

function FileContents(props: ContentsProps) {
    return <span>File content...</span>;
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
                        <DirectoryContents file={filesListVars.data.filesFilesByPath} storageId={storageId} parts={parts}/>
                    ) : (filesListVars.data.filesFilesByPath.type === "FILE") ? (
                        <FileContents file={filesListVars.data.filesFilesByPath} storageId={storageId} parts={parts}/>
                    ) : (filesListVars.data.filesFilesByPath.type === "LINK") ? (
                        <LinkContents file={filesListVars.data.filesFilesByPath} storageId={storageId} parts={parts}/>
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
