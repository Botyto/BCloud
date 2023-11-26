import { assert } from 'console';
import React from 'react';

interface NoteContentProps {
    note: any;
    editable?: boolean;
    onEdit?: (newContent: string) => void;
}

export default function NoteContent(props: NoteContentProps) {
    const lines = props.note.content.split('\n');
    console.log("lines", lines);
    function onEditLine(e: React.FocusEvent<HTMLDivElement>, index: number) {
        if (!props.onEdit) {
            throw new Error('onEdit is not defined');
        }
        const newLines = [...lines];
        const addedLines = e.target.innerText.split('\n');
        newLines.splice(index, 1, ...addedLines);
        console.log("new lines", newLines);
        const newContent = newLines.join('\n');
        props.onEdit(newContent);
    }

    if (props.editable && props.onEdit) {
        return lines.map((line: string, index: number) => {
            return <div
                key={index}
                contentEditable={true}
                suppressContentEditableWarning={true}
                onBlur={(e) => onEditLine(e, index)}
            >
                {line}
            </div>
        });
    } else {
        return <div>
            {props.note.content}
        </div>
    }
};
