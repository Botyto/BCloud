import React from 'react';
import fspath from '../../fspath';
import { ContentsProps } from '../common';
import FileEntry from './FileEntry';
import DirControls from './DirControls';

export default function DirectoryContents(props: ContentsProps) {
    const [selectedPaths, setSelectedPaths] = React.useState<string[]>([]);

    function setSelectedSinglePath(path: string, selected: boolean) {
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

    return <>
        <div>
            <div>
                <input
                    type="checkbox"
                    checked={allSelected}
                    onChange={toggleSelectAllPaths}
                    ref={input => {
                        if (!input) { return; }
                        input.indeterminate = partlySelected;
                    }}
                />
            </div>
            {
                (props.file.children.length === 0) ? (
                    <span>Empty...</span>
                ) : (props.file.children.map((file: any) => {
                        const path = fspath.join(null, [props.path, file.name]);
                        return <FileEntry
                            file={file}
                            path={path}
                            selected={selectedPaths.includes(path)}
                            onSelect={(s) => setSelectedSinglePath(path, s)}
                            key={file.id}
                        />;
                    })
                )
            }
        </div>
        <DirControls path={props.path} />
    </>;
}
