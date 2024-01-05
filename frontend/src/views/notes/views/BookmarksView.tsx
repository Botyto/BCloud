import React from 'react';
import { useTranslation } from 'react-i18next';
import { CollectionViewProps } from './types';
import { useNotesListQuery } from './api';
import Loading from '../../../components/Loading';

interface BookmarkProps {
    note: any;
}

function Bookmark(props: BookmarkProps) {
    return <div style={{display: "inline-block"}}>
        {props.note.title}
    </div>
}

export default function BookmarksView(props: CollectionViewProps) {
    const { t } = useTranslation("common");
    const notesData = useNotesListQuery(props.collection.slug, 0);
    
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
                        {t("notes.view.bookmarks.empty")}
                    </span>
                ) : (
                    notesData.data.notesNotesListBySlug.items.map((note: any) => {
                        return <Bookmark note={note}/>
                    })
                )
            }
        </div>
        <button>{t("notes.view.bookmarks.new.button")}</button>
    </div>;
}
