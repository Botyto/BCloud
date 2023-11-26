import React from 'react';

interface NoteContentProps {
    note: any;
    editable?: boolean;
    onEdit?: (newContent: string) => void;
}

export default function NoteContent(props: NoteContentProps) {
    if (props.editable && props.onEdit) {
        return <textarea
            value={props.note.content}
            onChange={(e) => props.onEdit(e.target.value)}
        />;
    } else {
        return <div>
            {props.note.content}
        </div>
    }
};
