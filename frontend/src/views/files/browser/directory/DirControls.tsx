import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import fspath from '../../fspath';
import { useFilesMakedirsMutation, useFilesMakefileMutation } from '../../filesApi';
import { Dialog, bindState, useDialogState } from '../../../../components/Dialog';
import { SERVER_HOST } from '../../../../ApiManagement';

const CREATING = "creating";
const UPLOADING = "uploading";
const COMPLETED = "completed";

interface FileUploadState {
    name: string;
    total: number;
    uploaded: number;
    status: string;
}

interface DirControlsProps {
    path: string;
}

export default function DirControls(props: DirControlsProps) {
    const { t } = useTranslation("common");
    const [storageId, parts] = fspath.getParts(props.path);
    const [makefile, makefileVars] = useFilesMakefileMutation();
    const [makedirs, makedirsVars] = useFilesMakedirsMutation();

    function onNewFile(e: React.MouseEvent) {
        e.preventDefault();
        const name = prompt(t("files.browser.dir.new_file.prompt"), "newfile.txt");
        if (!name) { return; }
        const newPath = fspath.join(storageId, [...parts, name])
        makefile({
            variables: {
                path: newPath,
                mimeType: "text/plain",
            },
            onError: (e) => {
                alert(e.message);
            },
        });
    }

    function onNewDir(e: React.MouseEvent) {
        e.preventDefault();
        const name = prompt(t("files.browser.dir.new_dir.prompt"), "newdir");
        if (!name) { return; }
        const newPath = fspath.join(storageId, [...parts, name])
        makedirs({
            variables: {
                path: newPath,
            },
            onError: (e: any) => {
                alert(e.message);
            },
        });
    }

    const uploadDialog = useDialogState();
    const [uploadFiles, setUploadFiles] = useState<FileUploadState[]>([]);
    const uploadRef = useRef<HTMLInputElement>(null);

    function addUploadFile(file: File) {
        setUploadFiles((files) => [
            ...files,
            {
                name: file.name,
                total: file.size,
                uploaded: 0,
                status: CREATING,
            },
        ]);
    }

    function updateUploadFile(file: File, uploaded: number) {
        setUploadFiles((files) => files.map((f) => f.name === file.name ? { ...f, uploaded } : f));
    }

    function setFileStatus(file: File, status: string) {
        setUploadFiles((files) => files.map((f) => f.name === file.name ? { ...f, status } : f));
    }

    useEffect(() => {
        if (uploadFiles.length === 0) { return;}
        const incompleteStatuses = [CREATING, UPLOADING];
        for (const file of uploadFiles) {
            if (incompleteStatuses.includes(file.status)) {
                return;
            }
        }
        uploadDialog.close();
        setUploadFiles([])
    }, [uploadFiles]);

    function onUpload(e: React.MouseEvent) {
        e.preventDefault();
        if (!uploadRef.current) { return; }
        uploadRef.current.click();
    }

    function doUpload() {
        if (!uploadRef.current?.files) { return; }
        if (uploadRef.current.files.length === 0) { return; }
        uploadDialog.open();
        for (var i = 0; i < uploadRef.current.files.length; ++i) {
            const file = uploadRef.current.files[i];
            const path = fspath.join(storageId, [...parts, file.name]);
            const contentUrl = fspath.pathToUrl(`${SERVER_HOST}/api/files/contents/:storageId/*`, path)
            addUploadFile(file);
            makefile({
                variables: { path, mimeType: file.type },
                onCompleted: () => {
                    setFileStatus(file, UPLOADING);
                    axios.post(contentUrl, file, {
                        headers: {
                            "Authorization": `Bearer ${localStorage.getItem('authentication-token')}`,
                            "Content-Type": file.type,
                        },
                        onUploadProgress: (e) => { updateUploadFile(file, e.loaded); },
                    }).then((r) => {
                        if (r.status === 200) { setFileStatus(file, COMPLETED); }
                    }).catch((e: object) => {
                        setFileStatus(file, e.toString());
                    });
                },
                onError: (e) => { alert("Error:\n" + e.message); },
            });
        }
    }

    return <div>
        <button onClick={onNewFile}>{t("files.browser.dir.new_file.button")}</button>
        <button onClick={onNewDir}>{t("files.browser.dir.new_dir.button")}</button>
        <input type="file" ref={uploadRef} onChange={doUpload} multiple hidden/>
        <button onClick={onUpload}>{t("files.browser.dir.upload.button")}</button>
        <Dialog {...bindState(uploadDialog)} style={{background: "white"}}>
            {
                uploadFiles.map((file) => {
                    return <div key={file.name} style={{border: "1px solid black", margin: "0.1rem"}}>
                        <span style={{display: "inline-block", minWidth: "10rem"}}>{file.name}</span>
                        <span style={{display: "inline-block", minWidth: "5rem"}}>{file.status}</span>
                        <span style={{display: "inline-block", minWidth: "5rem"}}>{file.uploaded}/{file.total}</span>
                    </div>
                })
            }
        </Dialog>
    </div>;
}
