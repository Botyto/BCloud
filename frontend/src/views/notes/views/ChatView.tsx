import React from 'react';
import { useTranslation } from 'react-i18next';
import { CollectionViewProps } from './types';
import { useNotesListQuery } from './api';
import Loading from '../../../components/Loading';

interface EntryProps {
    note: any;
}

function Entry(props: EntryProps) {
    return <div style={{display: "inline-block"}}>
        {props.note.title}
    </div>
}

export default function ChatView(props: CollectionViewProps) {
    const { t } = useTranslation("common");
    const notesData = useNotesListQuery(props.collection.id, 0);
    
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
                        {t("notes.notes.chat.empty")}
                    </span>
                ) : (
                    notesData.data.notesNotesList.items.map((note: any) => {
                        return <Entry note={note}/>
                    })
                )
            }
        </div>
        <div>
            <input type="text" placeholder={t("notes.notes.chat.new.placeholder")}/>
            <button>{t("notes.notes.chat.new.button")}</button>
        </div>
    </div>;
}
