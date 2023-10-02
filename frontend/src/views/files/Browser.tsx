import React from 'react';
import { Link, useParams } from 'react-router-dom';
import Loading from '../../components/Loading';
import { useFilesListQuery } from './filesApi';
import fspath from './fspath';

export default function Browser() {
    const params = useParams();
    const storageId = params.storageId || "";
    const filePath = params["*"] || "";
    const [_, parts] = fspath.getParts(filePath);
    if (parts.length > 0) {
        parts[0] = fspath.sep + parts[0];
    }
    const fullPath = fspath.join(storageId, parts);
    const filesListVars = useFilesListQuery(fullPath);

    return <>
        <div>Browser (<Link to="/files">storages</Link>)</div>
        <div>Path: {fspath.join(storageId, parts)}</div>
        <div>
            <ol>
                {
                    (filesListVars.loading) ? (
                        <Loading/>
                    ) : (filesListVars.error) ? (
                            <span style={{ color: "red" }}>Error: {filesListVars.error.message}</span>
                    ) : (filesListVars.data.filesFilesByPath.children.length === 0) ? (
                        <span>Empty...</span>
                    ) : (filesListVars.data.filesFilesByPath.children.map((file: any) => {
                        return <li>
                            {file.name}
                        </li>;
                    }))
                }
            </ol>
        </div>
    </>;
}
