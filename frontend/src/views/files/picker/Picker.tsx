import React from 'react';
import { useTranslation } from 'react-i18next';
import fspath from '../fspath';
import { useFilesListQuery, useFilesMakedirsMutation } from '../filesApi';
import Loading from '../../../components/Loading';

interface PickerEntryProps {
    file: any;
    path: string;
    disabled: boolean;
    onClick: () => void;
}

function PickerEntry(props: PickerEntryProps) {
    if (props.disabled) {
        return <div style={{textDecoration: "underline", cursor: "pointer", color: "gray"}}>
            {props.file.name}
        </div>;
    } else {
        return <div
            style={{textDecoration: "underline", cursor: "pointer", color: "blue"}}
            onClick={() => props.onClick()}
        >
            {props.file.name}
        </div>;
    }
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
    disabledPaths?: string[];
    allowNewDirectory?: boolean;
}

export default function Picker(props: PickerProps) {
    const { t } = useTranslation("common");
    const [path, setPath] = React.useState<string>(props.defaultPath);
    const [input, setInput] = React.useState<string>(props.inputDefault || "");
    const filesListVars = useFilesListQuery(path);
    const [makedirs, makedirsVars] = useFilesMakedirsMutation();

    function onNewDir(e: React.MouseEvent) {
        e.preventDefault();
        const name = prompt(t("files.browser.dir.new_dir.prompt"), "newdir");
        if (!name) { return; }
        const newPath = fspath.join(null, [path, name])
        makedirs({
            variables: {
                path: newPath,
            },
            onError: (e: any) => {
                alert(e.message);
            },
        });
    }

    return <div style={{background: "white", border: "1px solid black", padding: "0.3rem"}}>
        <div>{props.title}</div>
        <div style={{margin: "0.5rem"}}>
            <div>{path}</div>
            <div style={{ border: "solid 1px black" }}>
                {
                    (fspath.stripStorage(path)[1] !== "/") ? (
                        <PickerEntry
                            file={{name: ".."}}
                            path={fspath.dirName(path)}
                            disabled={false}
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
                            disabled={props.disabledPaths && props.disabledPaths.includes(filePath) || false}
                            onClick={() => {setPath(filePath)}}
                        />
                    }))
                }
            </div>
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
                (props.allowNewDirectory !== false) && <button onClick={onNewDir}>New directory</button>
            }
            {
                props.actions.map((action) => {
                    return <button key={action.name} onClick={() => {
                        if (props.input) {
                            action.onClick(fspath.join(null, [path, input]));
                        } else {
                            action.onClick(path);
                        }
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
