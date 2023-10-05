import React from 'react';
import { useTranslation } from 'react-i18next';
import fspath from '../../fspath';
import { ContentsProps } from '../common';
import { FileEntryHeader, FileEntry } from './FileEntry';
import DirControls from './DirControls';

export default function DirectoryContents(props: ContentsProps) {
    const { t } = useTranslation("common");
    const [selectedPaths, setSelectedPaths] = React.useState<string[]>([]);

    function setPathSelected(path: string, selected: boolean) {
        if (selected && !selectedPaths.includes(path)) {
            setSelectedPaths([...selectedPaths, path]);
        } else if (!selected && selectedPaths.includes(path)) {
            setSelectedPaths(selectedPaths.filter(p => p !== path));
        }
    }

    const allSelected = selectedPaths.length === props.file.children.length;
    const partlySelected = selectedPaths.length > 0 && !allSelected;
    function toggleSelectAllPaths() {
        if (allSelected) {
            setSelectedPaths([]);
        } else if (props.file.children) {
            setSelectedPaths(props.file.children.map(
                (file: any) => fspath.join(null, [props.path, file.name])
            ));
        }
    }

    function onRename(path: string) {
        const originalName = fspath.baseName(path);
        const name = prompt(t("files.browser.dir.file.rename.prompt", {name: originalName}), originalName);
        if (!name || name === originalName) { return; }
        //...
    }

    function onMove(paths: string[], single: boolean) { }

    function onCopy(paths: string[], single: boolean) { }

    function onDelete(paths: string[], single: boolean) {
        var title = "";
        if (single) {
            const name = fspath.baseName(paths[0]);
            title = t("files.browser.dir.file.delete.prompt", { name });
        } else {
            const count = paths.length;
            title = t("files.browser.dir.all.delete.prompt", { count });
        }
        const ok = window.confirm(title);
        if (!ok) { return; }
    }

    function onShare(path: string) { }

    function onAddLink(path: string) { }

    return <>
        <div>
            <div>
                <FileEntryHeader
                    allSelected={allSelected}
                    partlySelected={partlySelected}
                    toggleSelectAllPaths={toggleSelectAllPaths}
                    onMove={() => onMove(selectedPaths, false)}
                    onCopy={() => onCopy(selectedPaths, false)}
                    onDelete={() => onDelete(selectedPaths, false)}
                />
            </div>
            {
                (props.file.children.length === 0) ? (
                    <span>{t("files.browser.dir.empty")}</span>
                ) : (props.file.children.map((file: any) => {
                        const path = fspath.join(null, [props.path, file.name]);
                        return <FileEntry
                            file={file}
                            path={path}
                            selected={selectedPaths.includes(path)}
                            onSelect={(s) => setPathSelected(path, s)}
                            onRename={() => onRename(path)}
                            onMove={() => onMove([path], true)}
                            onCopy={() => onCopy([path], true)}
                            onDelete={() => onDelete([path], true)}
                            onShare={() => onShare(path)}
                            onAddLink={() => onAddLink(path)}
                            key={file.id}
                        />;
                    })
                )
            }
        </div>
        <DirControls path={props.path} />
    </>;
}
