import React from 'react';
import { Link, useParams } from 'react-router-dom';
import fspath from './fspath';

export default function Browser() {
    const params = useParams();
    const storageId = params.storageId || "";
    const filePath = params["*"] || "";
    const [_, parts] = fspath.getParts(filePath);
    if (parts.length > 0) {
        parts[0] = fspath.sep + parts[0];
    }
    return <>
        <div>Browser (<Link to="/files">storages</Link>)</div>
        <div>Path: {fspath.join(storageId, parts)}</div>
        <div>
            <ol>
                ... files here ...
            </ol>
        </div>
    </>;
}
