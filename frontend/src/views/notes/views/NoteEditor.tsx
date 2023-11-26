import React from 'react';
import { useTranslation } from 'react-i18next';

interface NoteEditorProps {
    note: any;
    setNote: (note: any) => void;
    onSave: () => void;
}

export default function NoteEditor(props: NoteEditorProps) {
    const { t } = useTranslation("common");

    function setNoteTitle(e: React.ChangeEvent<HTMLInputElement>) {
        props.setNote({
            ...props.note,
            title: e.target.value,
        });
    }

    function setNoteContent(e: React.ChangeEvent<HTMLTextAreaElement>) {
        props.setNote({
            ...props.note,
            content: e.target.value,
        });
    }

    return <div>
        <div>
            <input
                type="text"
                value={props.note.title}
                onChange={setNoteTitle}
            />
        </div>
        <div>
            <textarea
                value={props.note.content}
                onChange={setNoteContent}
            />
        </div>
        <div>
            <button onClick={() => props.onSave()}>
                {t("notes.view.notes.edit.save")}
            </button>
        </div>
    </div>;
}
