import React from 'react';
import { Link } from 'react-router-dom';
import fspath from '../fspath';
import { ContentsProps, BROWSER_ROUTE } from './common';
import { useFilesMakedirsMutation, useFilesMakefileMutation } from '../filesApi';
import MimeTypeIcon from './MimeTypeIcon';

export default function DirectoryContents(props: ContentsProps) {
    const [storageId, parts] = fspath.getParts(props.path);
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
            onError: (e: any) => {
                alert(e.message);
            },
        });
    }

    return <>
        <div>
            {
                (props.file.children.length === 0) ? (
                    <span>Empty...</span>
                ) : (props.file.children.map((file: any) => {
                        return <li key={file.id}>
                            <MimeTypeIcon type={file.type} mimeType={file.mimeType}/>
                            <Link to={fspath.pathToUrl(BROWSER_ROUTE, fspath.join(null, [props.path, file.name]))}>
                                {file.name}
                            </Link>
                        </li>;
                    })
                )
            }
        </div>
        <div>
            <button onClick={onNewFile}>New file</button>
            <button onClick={onNewDir}>New directory</button>
        </div>
    </>;
}
