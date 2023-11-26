import React from 'react';

interface NoteContentProps {
    note: any;
    editable?: boolean;
    onEdit?: (newContent: string) => void;
}

export default function NoteContent(props: NoteContentProps) {
    if (props.editable && props.onEdit) {
        const onEdit = props.onEdit; // to avoid ESLint warning
        return <textarea
            value={props.note.content}
            onChange={(e) => onEdit(e.target.value)}
        />;
    } else {
        return <div>
            {props.note.content}
        </div>
    }
};
