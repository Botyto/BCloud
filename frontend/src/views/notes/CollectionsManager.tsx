import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import CollectionsTree from './CollectionsTree';
import { Dialog, bindState, bindTrigger, useDialogState } from '../../components/Dialog';
import { useCollectionsNewMutation } from './api';

export default function CollectionsManager() {
    const { t } = useTranslation("common");
    const [newCollection, newCollectionData] = useCollectionsNewMutation();
    const addCollectionDlg = useDialogState();
    const [newCollectionName, setNewCollectionName] = useState<string>("");
    const [newCollectionView, setNewCollectionView] = useState<string>("NOTES");
    
    function cancelAddCollection(e: React.MouseEvent<HTMLButtonElement>) {
        e.preventDefault();
        addCollectionDlg.close()
        setNewCollectionName("");
    }

    function addCollection(e: React.MouseEvent<HTMLButtonElement>) {
        e.preventDefault();
        addCollectionDlg.close();
        if (newCollectionName.trim() === "") {
            return;
        }
        newCollection({
            variables: {
                name: newCollectionName.trim(),
                view: newCollectionView,
            },
        });
        setNewCollectionName("");
    }

    return <>
        <CollectionsTree/>
        <button {...bindTrigger(addCollectionDlg)}>{t("notes.collections.new.button")}</button>
        <Dialog {...bindState(addCollectionDlg)}>
            <input
                type="text"
                placeholder={t("notes.collections.new.name")}
                value={newCollectionName}
                onChange={(e) => setNewCollectionName(e.target.value)}
            />
            <select value={newCollectionView} onChange={(e) => setNewCollectionView(e.target.value)}>
                <option value="NOTES">{t("notes.collections.new.view.notes")}</option>
                <option value="BOOKMARKS">{t("notes.collections.new.view.bookmarks")}</option>
                <option value="CHAT">{t("notes.collections.new.view.chat")}</option>
            </select>
            <button onClick={cancelAddCollection}>{t("notes.collections.new.cancel")}</button>
            <button onClick={addCollection}>{t("notes.collections.new.add")}</button>
        </Dialog>
    </>
};