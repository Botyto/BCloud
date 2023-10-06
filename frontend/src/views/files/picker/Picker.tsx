import React from 'react';
import { useFilesListQuery } from '../filesApi';
import fspath from '../fspath';
import Loading from '../../../components/Loading';

interface PickerEntryProps {
    file: any;
    path: string;
    onClick: () => void;
}

function PickerEntry(props: PickerEntryProps) {
    return <div
        style={{textDecoration: "underline", cursor: "pointer", color: "blue"}}
        onClick={() => props.onClick()}
    >
        {props.file.name}
    </div>;
}

interface PickerAction {
    name: string;
    onClick: (path: string) => void;
}

interface PickerProps {
    title: string;
    defaultPath: string;
    actions: PickerAction[];
    cancelAfterAction?: boolean;
    onCancel: () => void;
    showTypes?: string[];
    input?: boolean;
    inputLabel?: string;
    inputDefault?: string;
}

export default function Picker(props: PickerProps) {
    const [path, setPath] = React.useState<string>(props.defaultPath);
    const [input, setInput] = React.useState<string>(props.inputDefault || "");
    const filesListVars = useFilesListQuery(path);

    return <div style={{background: "white", border: "1px solid black", padding: "0.3rem"}}>
        <div>{props.title}</div>
        <div>{path}</div>
        <div>
            {
                (fspath.stripStorage(path)[1] !== "/") ? (
                    <PickerEntry
                        file={{name: ".."}}
                        path={fspath.dirName(path)}
                        onClick={() => {setPath(fspath.dirName(path))}}
                    />
                ) : null
            }
            {
                (filesListVars.loading) ? (
                    <Loading/>
                ) : (filesListVars.error) ? (
                    <div style={{color: "red"}}>Error: {filesListVars.error.message}</div>
                ): (filesListVars.data.filesFilesByPath.children
                    .filter((file: any) => {
                        if (!props.showTypes) { return true; }
                        return props.showTypes.includes(file.type);
                    })
                    .map((file: any) => {
                    const filePath = fspath.join(null, [path, file.name]);
                    return <PickerEntry
                        key={file.id}
                        file={file}
                        path={filePath}
                        onClick={() => {setPath(filePath)}}
                    />
                }))
            }
        </div>
        {
            props.input && <div>
                {
                    props.inputLabel && <span>{props.inputLabel}: </span>
                }
                <input type="text" value={input} onChange={(e) => setInput(e.target.value)} />
            </div>
        }
        <div>
            {
                props.actions.map((action) => {
                    return <button key={action.name} onClick={() => {
                        action.onClick(path);
                        if (props.cancelAfterAction !== false) { props.onCancel(); }
                    }} >
                        {action.name}
                    </button>;
                })
            }
            <button onClick={() => props.onCancel()}>Cancel</button>
        </div>
    </div>;
}