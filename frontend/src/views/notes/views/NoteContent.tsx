import React from 'react';
import ContentEditable, { ContentEditableEvent } from 'react-contenteditable';
import { mdToHtml, htmlToMd } from './Markdown';

interface NoteContentProps {
    note: any;
    editable?: boolean;
    onEdit?: (newContent: string) => void;
}

export default function NoteContent(props: NoteContentProps) {
    const handleChange = (e: ContentEditableEvent) => {
        props.onEdit(htmlToMd(e.target.value));
    };

    const html = mdToHtml(props.note.content);
    const canEdit = Boolean(props.editable && props.onEdit);
    return <ContentEditable
        html={html}
        onChange={handleChange}
        disabled={!canEdit}
    />;
};
