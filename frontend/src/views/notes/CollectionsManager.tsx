import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import CollectionsTree from './CollectionsTree';
import { Dialog, bindState, useDialogState } from '../../components/Dialog';
import { useCollectionsNewMutation } from './api';

export default function CollectionsManager() {
    const { t } = useTranslation("common");
    const [newCollection, newCollectionData] = useCollectionsNewMutation();
    const addCollectionDlg = useDialogState();
    const [newCollectionName, setNewCollectionName] = useState<string>("");
    
    function cancelAddCollection(e: React.MouseEvent<HTMLButtonElement>) {
        e.preventDefault();
        addCollectionDlg.close()
        setNewCollectionName("");
    }

    function addCollection(e: React.MouseEvent<HTMLButtonElement>) {
        e.preventDefault();
        addCollectionDlg.close();
        const name = newCollectionName.trim();
        setNewCollectionName("");
        newCollection({
            variables: {
                name: name,
                view: "NOTES",
            },
        });
    }

    return <>
        <CollectionsTree/>
        <button onClick={() => addCollectionDlg.open()}>new collection</button>
        <Dialog {...bindState(addCollectionDlg)}>
            <input
                type="text"
                placeholder={t("notes.collections.new.name")}
                value={newCollectionName}
                onChange={(e) => setNewCollectionName(e.target.value)}
            />
            <button onClick={cancelAddCollection}>{t("notes.collections.new.cancel")}</button>
            <button onClick={addCollection}>{t("notes.collections.new.add")}</button>
        </Dialog>
    </>
};