import React from 'react';
import { Link } from 'react-router-dom';
import Loading from '../../components/Loading';
import { useStorageCreateMutation, useStorageListQuery } from './api';
import Pagination from '../../components/Pagination';

export default function Storages() {
    const [page, setPage] = React.useState(0);
    const storageListVars = useStorageListQuery(page);

    const [newStorageName, setNewStorageName] = React.useState('');
    const [newStorageError, setNewStorageError] = React.useState('');
    const [storageCreate, storageCreateVars] = useStorageCreateMutation();

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
                    return <li key={storage.id}>{storage.name}</li>;
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
