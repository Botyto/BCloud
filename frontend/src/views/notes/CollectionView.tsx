import React from 'react';
import Loading from '../../components/Loading';
import { useCollectionsGetQuery } from './api';
import { useTranslation } from 'react-i18next';
import NotesView from './views/NotesView';
import BookmarksView from './views/BookmarksView';
import ChatView from './views/ChatView';

interface CollectionViewProps {
    collectionSlug: string;
}

export default function CollectionView(props: CollectionViewProps) {
    const { t } = useTranslation("common");
    const collectionData = useCollectionsGetQuery(props.collectionSlug);

    if (collectionData.loading) {
        return <Loading/>;
    } else if (collectionData.error) {
        return <span style={{color: "red"}}>
            {t("notes.collection.error", { error: collectionData.error.message })}
        </span>;
    } else {
        const collection = collectionData.data.notesCollectionsGetBySlug;
        return <div>
            <span>{t("notes.collection.title", { name: collection.name })}</span>
            {
                (collection.view == "NOTES") ? (
                    <NotesView collection={collection}/>
                ) : (collection.view == "BOOKMARKS") ? (
                    <BookmarksView collection={collection}/>
                ) : (collection.view == "CHAT") ? (
                    <ChatView collection={collection}/>
                ) : (
                    <NotesView collection={collection}/>
                )
            }
            
        </div>;
    }
}