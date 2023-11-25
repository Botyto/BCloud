import React from 'react';
import { Link } from "react-router-dom";
import { useTranslation } from 'react-i18next';
import CollectionsView from './CollectionsView';

export default function NotesBrowser() {
    const { t } = useTranslation("common");

    return <div>
        <div>
            {t("notes.title")} (<Link to="/">{t("notes.back_to_homepage")}</Link>)
        </div>
        <CollectionsView/>
    </div>;
}