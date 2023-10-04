import React from 'react';
import fspath from '../../fspath';
import { useFilesMakedirsMutation, useFilesMakefileMutation } from '../../filesApi';

interface DirControlsProps {
    path: string;
}

export default function DirControls(props: DirControlsProps) {
    const [storageId, parts] = fspath.getParts(props.path);
    const [makefile, makefileVars] = useFilesMakefileMutation();
    const [makedirs, makedirsVars] = useFilesMakedirsMutation();

    function onNewFile(e: React.MouseEvent) {
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

    function onNewDir(e: React.MouseEvent) {
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

    return <div>
        <button onClick={onNewFile}>New file</button>
        <button onClick={onNewDir}>New directory</button>
    </div>;
}
