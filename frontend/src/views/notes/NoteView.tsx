import React from 'react';

interface NoteViewProps {
    noteId: string;
}

export default function NoteView(props: NoteViewProps) {
    return <div>Note View {props.noteId}</div>;
}