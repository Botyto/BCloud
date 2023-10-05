import React from 'react';
import { useTranslation } from 'react-i18next';
import fspath from '../../fspath';
import { useFilesMakedirsMutation, useFilesMakefileMutation } from '../../filesApi';

interface DirControlsProps {
    path: string;
}

export default function DirControls(props: DirControlsProps) {
    const { t } = useTranslation("common");
    const [storageId, parts] = fspath.getParts(props.path);
    const [makefile, makefileVars] = useFilesMakefileMutation();
    const [makedirs, makedirsVars] = useFilesMakedirsMutation();

    function onNewFile(e: React.MouseEvent) {
        e.preventDefault();
        const name = prompt(t("files.browser.dir.new_file.prompt"), "newfile.txt");
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
        const name = prompt(t("files.browser.dir.new_dir.prompt"), "newdir");
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
        <button onClick={onNewFile}>{t("files.browser.dir.new_file.button")}</button>
        <button onClick={onNewDir}>{t("files.browser.dir.new_dir.button")}</button>
    </div>;
}
