import React from 'react';

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

    return <div style={{background: "white", border: "1px solid black", padding: "0.3rem"}}>
        <div>{props.title}</div>
        <div>
            ...
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
