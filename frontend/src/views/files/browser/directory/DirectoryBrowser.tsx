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

    function onMoveSelected() { }

    function onCopySelected() { }

    function onDeleteSelected() {
        const count = selectedPaths.length;
        const ok = window.confirm(t("files.browser.dir.all.delete.prompt", {count}));
    }

    return <>
        <div>
            <div>
                <FileEntryHeader
                    allSelected={allSelected}
                    partlySelected={partlySelected}
                    toggleSelectAllPaths={toggleSelectAllPaths}
                    onMove={onMoveSelected}
                    onCopy={onCopySelected}
                    onDelete={onDeleteSelected}
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
                            key={file.id}
                        />;
                    })
                )
            }
        </div>
        <DirControls path={props.path} />
    </>;
}
