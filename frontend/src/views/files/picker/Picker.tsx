import React from 'react';
import { useFilesListQuery } from '../filesApi';
import Loading from '../../../components/Loading';

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
}

export default function Picker(props: PickerProps) {
    const [path, setPath] = React.useState<string>(props.defaultPath);
    const filesListVars = useFilesListQuery(path);

    return <div style={{background: "white", border: "1px solid black", padding: "0.3rem"}}>
        <div>{props.title}</div>
        <div>
            {
                (filesListVars.loading) ? (
                    <Loading/>
                ) : (filesListVars.error) ? (
                    <div style={{color: "red"}}>Error: {filesListVars.error.message}</div>
                ): (filesListVars.data.filesFilesByPath.children.map((file: any) => {
                    {JSON.stringify(file)}
                }))
            }
        </div>
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
