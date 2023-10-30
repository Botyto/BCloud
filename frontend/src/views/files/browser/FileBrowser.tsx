import React from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import fspath from '../fspath';
import { ContentsProps } from './common';
import { GetPreview } from '../previews/preview';
import TxtPreview from '../previews/TxtPreview';
import AudioPreview from '../previews/AudioPreview';
import VideoPreview from '../previews/VideoPreview';
import ImagePreview from '../previews/ImagePreview';
import PdfPreview from '../previews/PdfPreview';
import ArchivePreview from '../previews/ArchivePreview';

export default function FileBrowser(props: ContentsProps) {
    const { t } = useTranslation("common");
    function download(e: React.MouseEvent, url: string, name: string) {
        e.preventDefault();
        axios.get(url, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authentication-token')}`
            },
            responseType: 'blob',
        })
        .then((r) => {
            const url = window.URL.createObjectURL(r.data);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = name;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        })
        .catch((e) => {
            alert(e.message);
        });
    }
    
    const SERVER_HOST = import.meta.env.VITE_BACKEND_URL;
    const downloadUrl = fspath.pathToUrl(`${SERVER_HOST}/api/files/download/:storageId/*`, props.path)
    const contentUrl = fspath.pathToUrl(`${SERVER_HOST}/api/files/contents/:storageId/*`, props.path)
    const name = fspath.baseName(props.path);
    const Preview = GetPreview(props.file, [
        TxtPreview,
        AudioPreview,
        VideoPreview,
        ImagePreview,
        PdfPreview,
        ArchivePreview,
    ]);

    if (props.file.size === null) {
        return <div>{t("files.browser.file.no_content")}</div>;
    }

    return <>
        <button onClick={e => download(e, downloadUrl, name)}>{t("files.browser.file.download")}</button>
        <Preview file={props.file} path={props.path} contentUrl={contentUrl}/>
    </>;
}
