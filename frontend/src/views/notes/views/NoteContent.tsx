import React from 'react';

interface NoteContentProps {
    note: any;
    editable?: boolean;
    listEdit?: boolean;
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

    function onEditWhole(e: React.FocusEvent<HTMLDivElement>) {
        if (!props.onEdit) {
            throw new Error('onEdit is not defined');
        }
        props.onEdit(e.target.innerText);
    }

    if (props.editable && props.onEdit) {
        if (props.listEdit) {
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
            return <div
                contentEditable={true}
                suppressContentEditableWarning={true}
                onBlur={(e) => onEditWhole(e)}
            >
                {props.note.content.split("\n").map((line: string, index: number) => {
                    if (line.trimEnd() !== "") {
                        return <div key={index}>{line.trimEnd()}</div>;
                    }
                })}
            </div>
        }
    } else {
        return <div>
            {props.note.content.split("\n").map((line: string, index: number) => (
                <div key={index}>{line}</div>
            ))}
        </div>
    }
};
