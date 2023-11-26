import React from 'react';
import { useTranslation } from 'react-i18next';
import NoteContent from './NoteContent';

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

    function setNoteContent(newContent: string) {
        props.setNote({
            ...props.note,
            content: newContent,
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
            <NoteContent
                note={props.note}
                editable={true}
                onEdit={setNoteContent}
            />
        </div>
        <div>
            <button onClick={() => props.onSave()}>
                {t("notes.view.notes.edit.save")}
            </button>
        </div>
    </div>;
}
