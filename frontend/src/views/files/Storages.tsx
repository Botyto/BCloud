import React from 'react';
import { Link } from 'react-router-dom';
import Loading from '../../components/Loading';
import { useStorageCreateMutation, useStorageDeleteMutation, useStorageListQuery, useStorageRenameMutation } from './storageApi';
import Pagination from '../../components/Pagination';

export default function Storages() {
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
        const name = prompt('New name', storage.name);
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
            Storages (<Link to="/">homepage</Link>)<br/>
            <Loading/>
        </span>;
    } else if (storageListVars.error) {
        return <span>
            Storages (<Link to="/">homepage</Link>)
            <span style={{color: "red"}}>{storageListVars.error.message}</span>
        </span>;
    } else {
        return <>
            <div>
                Storages (<Link to="/">homepage</Link>)
            </div>
            <ul>
                {storageListVars.data?.filesStorageList.items.map((storage: any) => {
                    return <li key={storage.id}>
                        {storage.name}
                        - <Link to={`/files/${storage.slug}/`}>browse</Link>
                        - <button onClick={e => onRename(e, storage)}>rename</button>
                        - <button onClick={e => onDelete(e, storage)}>delete</button>
                        {
                            storageErrors[storage.id] &&
                            <span style={{color: "red"}}>{storageErrors[storage.id]}</span>
                        }
                    </li>;
                })}
            </ul>
            <Pagination {...storageListVars.data.filesStorageList} setPage={setPage} />
            <form onSubmit={onCreateStorage}>
                <input type="text" name="name" value={newStorageName} onChange={n => setNewStorageName(n.target.value)} />
                <button type="submit">Create</button>
                <div style={{color: "red"}}>{newStorageError}</div>
            </form>
        </>;
    }
}
