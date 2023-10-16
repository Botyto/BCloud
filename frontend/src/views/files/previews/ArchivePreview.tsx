import React from 'react';
import { PreviewProps, Preview, listMimeType } from './preview';
import { useArchivePreviewQuery } from './api';
import Loading from '../../../components/Loading';

function ArchivePreview(props: PreviewProps) {
    const filesVars = useArchivePreviewQuery(props.path);

    if (filesVars.loading) {
        return <Loading/>;
    } else if (filesVars.error) {
        return <span style={{color: "red"}}>{filesVars.error.message}</span>;
    } else {
        return (
            <div>
                {
                    filesVars.data.filesPreviewArchive.files.map((file: any) => {
                        return <div key={file.path}>{file.path} | {file.mime}</div>;
                    })
                }
            </div>
        );
    }
}

const archiveMimeTypes = [
    "application/zip",
    "application/x-zip-compressed",
];
export default new Preview(listMimeType(archiveMimeTypes), ArchivePreview, true);
