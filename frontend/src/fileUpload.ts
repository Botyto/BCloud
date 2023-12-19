import axios from "axios";
import { useState } from "react";

export enum Status {
    CREATING = "creating",
    UPLOADING = "uploading",
    FAILED = "failed",
    COMPLETED = "completed",
    NO_FILE = "nofile",
}

export interface FileUploadStateInternal {
    file: File;
    total: number;
    uploaded: number;
    status: string;
}

export class FileUploadState {
    file: File|null;
    total: number;
    uploaded: number;
    status: string;
    setProgress: (uploadedBytes: number) => void;
    setStatus: (status: string) => void;
    reset: () => void;

    constructor(internal: FileUploadStateInternal|null, setProgress: (uploadedBytes: number) => void, setStatus: (status: string) => void, reset: () => void) {
        if (internal) {
            this.file = internal.file;
            this.total = internal.total;
            this.uploaded = internal.uploaded;
            this.status = internal.status;
        } else {
            this.file = null;
            this.total = 0;
            this.uploaded = 0;
            this.status = Status.NO_FILE;
        }
        this.setProgress = setProgress;
        this.setStatus = setStatus;
        this.reset = reset;
    }

    isError() {
        return !Object.values(Status).includes(this.status);
    }
}

export function useFileUploadState() {
    const [state, setState] = useState<FileUploadStateInternal|null>(null);
    const setProgress = (uploadedBytes: number) => {
        if (state) {
            setState({
                ...state,
                uploaded: uploadedBytes,
            });
        }
    };
    const setStatus = (status: string) => {
        if (state) {
            setState({
                ...state,
                status: status,
            });
        }
    };
    const reset = () => {
        setState(null);
    }
    return new FileUploadState(state, setProgress, setStatus, reset);
}

export function uploadFile(path: string, file: File) {
    onUpdate(UPLOADING);
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
}
