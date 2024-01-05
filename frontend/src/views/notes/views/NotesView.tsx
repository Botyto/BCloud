import React from 'react';
import { useTranslation } from 'react-i18next';
import Loading from '../../../components/Loading';
import { Dialog, useDialogState, bindState } from '../../../components/Dialog';
import { CollectionViewProps } from './types';
import { useNotesListQuery, useCreateNoteMutation } from './api';
import NoteEditor from './NoteEditor';
import NoteContent from './NoteContent';

interface NoteProps {
    note: any;
    onEdit: () => void;
}

function Note(props: NoteProps) {
    return <div
        style={{
            display: "inline-block",
            border: "1px solid black",
            margin: "1rem",
            padding: "1rem",
            backgroundColor: "#90e0e0",
        }}
        onClick={() => props.onEdit()}
    >
        <div style={{textDecoration: "underline", fontWeight: "bold"}}>
            {props.note.title}
        </div>
        <NoteContent note={props.note}/>
    </div>
}

export default function NotesView(props: CollectionViewProps) {
    const { t } = useTranslation("common");
    const editorDlg = useDialogState();
    const notesData = useNotesListQuery(props.collection.slug, 0);
    const [createNote, createNoteData] = useCreateNoteMutation();
    const [editedNote, setEditedNote] = React.useState<any>(null);
    
    function editNote(note: any) {
        setEditedNote(note);
        editorDlg.open();
    }

    function editNewNote() {
        setEditedNote({
            title: "",
            content: "",
        })
        editorDlg.open();
    }

    function saveNote() {
        if (editedNote.id) {
            alert("editing not implemented");
        } else {
            createNote({
                variables: {
                    collectionSlug: props.collection.slug,
                    title: editedNote.title,
                    content: editedNote.content,
                    tags: [],
                },
            });
        }
        editorDlg.close();
    }

    return <div>
        <div>
            {
                (notesData.loading) ? (
                    <Loading/>
                ) : (notesData.error) ? (
                    <span style={{color: "red"}}>
                        {t("notes.collection.error", {error: notesData.error.message})}
                    </span>
                ) : (notesData.data.notesNotesListBySlug.items.length == 0) ? (
                    <span>
                        {t("notes.view.notes.empty")}
                    </span>
                ) : (
                    notesData.data.notesNotesListBySlug.items.map((note: any) => {
                        return <Note
                            key={note.id}
                            note={note}
                            onEdit={() => editNote(note)}
                        />
                    })
                )
            }
        </div>
        <button onClick={() => editNewNote()}>
            {t("notes.view.notes.new.button")}
        </button>
        <Dialog {...bindState(editorDlg)}>
            <NoteEditor
                note={editedNote}
                setNote={(note: any) => setEditedNote(note)}
                onSave={() => saveNote()}
            />
        </Dialog>
    </div>;
}
