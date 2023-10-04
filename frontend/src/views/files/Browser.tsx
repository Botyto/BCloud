import React from 'react';
import { Link, useParams } from 'react-router-dom';
import Loading from '../../components/Loading';
import fspath from './fspath';
import { useFilesListQuery } from './filesApi';
import { Breadcrumbs, makeBreadcrumbs } from './Breadcrumbs';
import DirectoryBrowser from './browser/DirectoryBrowser';
import FileBrowser from './browser/FileBrowser';
import LinkBrowser from './browser/LinkBrowser';

export default function Browser() {
    const params = useParams();
    const storageId = params.storageId || "";
    const filePath = params["*"] || "";
    const [_, parts] = fspath.getParts(filePath);
    const fullPath = fspath.join(storageId, parts);
    const filesListVars = useFilesListQuery(fullPath);
    const breadcrumbs = makeBreadcrumbs(storageId, storageId, parts);

    return <>
        <div>Browser (<Link to="/files">storages</Link>)</div>
        <div>Path: <Breadcrumbs pieces={breadcrumbs}/></div>
        <div>
            {
                (filesListVars.loading) ? (
                    <Loading/>
                ) : (filesListVars.error) ? (
                    <span style={{ color: "red" }}>Error: {filesListVars.error.message}</span>
                ) : (filesListVars.data.filesFilesByPath.type === "DIRECTORY") ? (
                    <DirectoryBrowser file={filesListVars.data.filesFilesByPath} path={fullPath}/>
                ) : (filesListVars.data.filesFilesByPath.type === "FILE") ? (
                    <FileBrowser file={filesListVars.data.filesFilesByPath} path={fullPath}/>
                ) : (filesListVars.data.filesFilesByPath.type === "LINK") ? (
                    <LinkBrowser file={filesListVars.data.filesFilesByPath} path={fullPath}/>
                ) : (
                    <span>Unknown file type {filesListVars.data.filesFilesByPath.type}</span>
                )
            }
        </div>
    </>;
}
