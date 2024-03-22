import React, { useRef } from 'react';
import { useTranslation } from 'react-i18next';
import NoteContent from './NoteContent';

interface NoteEditorProps {
    note: any;
    setNote: (note: any) => void;
    onSave: () => void;
}

export default function NoteEditor(props: NoteEditorProps) {
    const { t } = useTranslation("common");
    const noteContent = useRef(props.note.content);

    function setNoteTitle(e: React.ChangeEvent<HTMLInputElement>) {
        props.setNote({
            ...props.note,
            title: e.target.value,
        });
    }

    function onSave() {
        props.setNote({
            ...props.note,
            content: noteContent.current,
        });
        props.onSave();
    }

    return <div style={{
        backgroundColor: props.note.color,
        padding: "1rem",
    }}>
        <div>
            <input
                type="text"
                value={props.note.title}
                onChange={setNoteTitle}
            />
        </div>
        <div style={{
            marginTop: "1rem",
            marginBottom: "1rem",
            border: "1px solid black",
        }}>
            <NoteContent
                editable={true}
                content={noteContent}
            />
        </div>
        <div>
            <button onClick={onSave}>
                {t("notes.view.notes.edit.save")}
            </button>
        </div>
    </div>;
}
