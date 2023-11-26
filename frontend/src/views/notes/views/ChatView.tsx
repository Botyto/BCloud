import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { CollectionViewProps } from './types';
import { useCreateNoteMutation, useNotesListQuery } from './api';
import Loading from '../../../components/Loading';

interface EntryProps {
    note: any;
}

function Entry(props: EntryProps) {
    return <div style={{
        border: "1px solid black",
        borderRadius: "0.5rem",
        backgroundColor: "#eee",
        margin: "0.5rem",
        padding: "0.5rem",
    }}>
        {props.note.content}
        <div style={{fontSize: "0.5rem"}}><i>{props.note.createdAtUtc}</i></div>
    </div>
}

export default function ChatView(props: CollectionViewProps) {
    const { t } = useTranslation("common");
    const notesData = useNotesListQuery(props.collection.id, 0);
    const [newNoteContent, setNewNoteContent] = useState<string>("");
    const [createNote, createNoteData] = useCreateNoteMutation();

    function saveNote(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        createNote({
            variables: {
                collectionId: props.collection.id,
                title: "",
                content: newNoteContent,
                tags: [],
            },
        })
        setNewNoteContent("");
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
                ) : (notesData.data.notesNotesList.items.length == 0) ? (
                    <span>
                        {t("notes.view.chat.empty")}
                    </span>
                ) : (
                    notesData.data.notesNotesList.items.map((note: any) => {
                        return <Entry key={note.id} note={note}/>
                    })
                )
            }
        </div>
        <form onSubmit={saveNote}>
            <input
                type="text"
                placeholder={t("notes.view.chat.new.placeholder")}
                value={newNoteContent}
                onChange={(e) => setNewNoteContent(e.target.value)}
            />
            <button type="submit">{t("notes.view.chat.new.button")}</button>
        </form>
    </div>;
}
