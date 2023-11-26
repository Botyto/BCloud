import React from 'react';
import { useParams } from 'react-router-dom'
import { Link } from "react-router-dom";
import { useTranslation } from 'react-i18next';
import CollectionsManager from './CollectionsManager';
import CollectionView from './CollectionView';
import NoteView from './NoteView';

export default function NotesBrowser() {
    const { t } = useTranslation("common");
    const routeParams = useParams();
    const collectionId = routeParams.collection;
    const noteId = routeParams.note;

    return <div>
        <div>
            {t("notes.title")} (<Link to="/">{t("notes.back_to_homepage")}</Link>)
        </div>
        <div>
            <span style={{display: "inline-block", verticalAlign: "top"}}>
                <CollectionsManager/>
            </span>
            <span style={{display: "inline-block"}}>
                {
                    (noteId) ? (
                        <NoteView noteId={noteId}/>
                    ) : (collectionId) ? (
                        <CollectionView collectionId={parseInt(collectionId)}/>
                    ) : (
                        <></>
                    )
                }
            </span>
        </div>
    </div>;
}