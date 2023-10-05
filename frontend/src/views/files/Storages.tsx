import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import Loading from '../../components/Loading';
import { useStorageCreateMutation, useStorageDeleteMutation, useStorageListQuery, useStorageRenameMutation } from './storageApi';
import Pagination from '../../components/Pagination';

export default function Storages() {
    const { t } = useTranslation("common");
    const [page, setPage] = React.useState(0);
    const storageListVars = useStorageListQuery(page);
    const [storageErrors, setStorageErrors] = React.useState<any>({});

    const [newStorageName, setNewStorageName] = React.useState('');
    const [newStorageError, setNewStorageError] = React.useState('');
    const [storageCreate, storageCreateVars] = useStorageCreateMutation();
    const [storageRename, storageRenameVars] = useStorageRenameMutation();
    const [storageDelete, storageDeleteVars] = useStorageDeleteMutation();

    function onCreateStorage(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        storageCreate({
            variables: {
                name: newStorageName,
            },
            onCompleted: () => {
                storageListVars.refetch();
            },
            onError: (e) => {
                setNewStorageError(e.message);
            },
        });
        setNewStorageError('');
        setNewStorageName('');
    }

    function onRename(e: React.MouseEvent<HTMLButtonElement>, storage: any) {
        e.preventDefault();
        const name = prompt(t("files.storages.rename.prompt", {name: storage.name}), storage.name);
        if (!name) { return; }
        storageRename({
            variables: {
                id: storage.id,
                name: name,
            },
            onCompleted: () => {
                storageListVars.refetch();
            },
            onError: (e) => {
                const newErrors: any = {...storageErrors};
                newErrors[storage.id] = e.message
                setStorageErrors(newErrors);
            },
        });
    }

    function onDelete(e: React.MouseEvent<HTMLButtonElement>, storage: any) {
        e.preventDefault();
        const ok = confirm(t("files.storages.delete.prompt", {name: storage.name}));
        if (!ok) { return; }
        storageDelete({
            variables: {
                id: storage.id,
            },
            onCompleted: () => {
                storageListVars.refetch();
            },
            onError: (e) => {
                const newErrors: any = {...storageErrors};
                newErrors[storage.id] = e.message
                setStorageErrors(newErrors);
            },
        });
    }

    if (storageListVars.loading) {
        return <span>
            {t("files.storages.title")} (<Link to="/">{t("files.storages.back_to_homepage")}</Link>)<br/>
            <Loading/>
        </span>;
    } else if (storageListVars.error) {
        return <span>
            {t("files.storages.title")} (<Link to="/">{t("files.storages.back_to_homepage")}</Link>)
            <span style={{color: "red"}}>{storageListVars.error.message}</span>
        </span>;
    } else {
        return <>
            <div>
                {t("files.storages.title")} (<Link to="/">{t("files.storages.back_to_homepage")}</Link>)
            </div>
            <div>
                {storageListVars.data?.filesStorageList.items.map((storage: any) => {
                    return <div key={storage.id}>
                        💽
                        <span style={{display: "inline-block", minWidth: "5rem"}}>{storage.name}</span>
                        <Link to={`/files/${storage.slug}/`}>{t("files.storages.browse")}</Link>
                        <button onClick={e => onRename(e, storage)}>{t("files.storages.rename.button")}</button>
                        <button onClick={e => onDelete(e, storage)}>{t("files.storages.delete.button")}</button>
                        {
                            storageErrors[storage.id] &&
                            <span style={{color: "red"}}>{storageErrors[storage.id]}</span>
                        }
                    </div>;
                })}
            </div>
            <Pagination {...storageListVars.data.filesStorageList} setPage={setPage} />
            <form onSubmit={onCreateStorage}>
                <input type="text" name="name" value={newStorageName} onChange={n => setNewStorageName(n.target.value)} />
                <button type="submit">{t("files.storages.create")}</button>
                <div style={{color: "red"}}>{newStorageError}</div>
            </form>
        </>;
    }
}
