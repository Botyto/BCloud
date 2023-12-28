import React, { useRef, useState } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { VisibilityObserver } from 'reactjs-visibility';
import { CollectionViewProps } from './types';
import { useAttachFileMutation, useCreateNoteMutation, useNotesListQuery } from './api';
import Loading from '../../../components/Loading';
import fspath from '../../files/fspath';
import { SERVER_HOST } from '../../../ApiManagement';

interface EntryProps {
    note: any;
}

function Entry(props: EntryProps) {
    return <div style={{
        border: "1px solid black",
        borderRadius: "0.5rem",
        backgroundColor: "#eee",
        margin: "0.5rem",
        padding: "0.5rem",
    }}>
        {
            props.note.files
                .filter((f: any) => f.kind === "ATTACHMENT")
                .map((f: any) => {
                    const contentUrl = fspath.pathToUrl(`${SERVER_HOST}/api/files/contents/:storageId/*`, f.file.abspath);
                    return <img key={f.id} src={contentUrl} />
                })
        }
        {props.note.content}
        <div style={{fontSize: "0.5rem"}}><i>{props.note.createdAtUtc}</i></div>
    </div>
}

const CREATING = "creating";
const UPLOADING = "uploading";
const COMPLETED = "completed";

interface FileUploadState {
    total: number;
    uploaded: number;
    status: string;
}

export default function ChatView(props: CollectionViewProps) {
    const { t } = useTranslation("common");
    const notesData = useNotesListQuery(props.collection.id, 0);
    const [newNoteContent, setNewNoteContent] = useState<string>("");
    const [imagePreviewFile, setImagePreviewFile] = useState<File|null>(null);
    const [imagePreviewUrl, setImagePreviewUrl] = useState<string>("");
    const [imageUploadState, setImageUploadState] = useState<FileUploadState|null>(null);
    const [createNote, createNoteData] = useCreateNoteMutation();
    const [attachNote, attachNoteData] = useAttachFileMutation();
    const container = useRef<HTMLDivElement>(null);

    if (container.current) {
        container.current.scrollTo(0, container.current.scrollHeight);
    }

    function saveNote(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        if (imagePreviewFile) {
            setImageUploadState({
                total: imagePreviewFile.size,
                uploaded: 0,
                status: CREATING,
            });
        }
        createNote({
            variables: {
                collectionId: props.collection.id,
                title: "",
                content: newNoteContent,
                tags: [],
            },
            onCompleted: (!imagePreviewFile) ? undefined : (data) => {
                attachNote({
                    variables: {
                        noteId: data.notesNotesCreate.id,
                        kind: "ATTACHMENT",
                        mimeType: imagePreviewFile.type,
                    },
                    onCompleted: (attachmentData) => {
                        const filePath = attachmentData.notesNoteattachmentsAddAttachment.file.abspath;
                        const contentUrl = fspath.pathToUrl(`${SERVER_HOST}/api/files/contents/:storageId/*`, filePath);
                        setImageUploadState({
                            ...imageUploadState!,
                            status: UPLOADING,
                        });
                        axios.post(contentUrl, imagePreviewFile, {
                            headers: {
                                "Authorization": `Bearer ${localStorage.getItem('authentication-token')}`,
                                "Content-Type": imagePreviewFile.type,
                            },
                            onUploadProgress: (e) => {
                                setImageUploadState({...imageUploadState!, uploaded: e.loaded});
                            },
                        }).then((r) => {
                            if (r.status === 200) {
                                setImageUploadState({...imageUploadState!, status: COMPLETED});
                                clearImagePreview();
                                setNewNoteContent("");
                            }
                        }).catch((e: object) => {
                            setImageUploadState({...imageUploadState!, status: e.toString()});
                        });
                    },
                })
            },
        })
        setNewNoteContent("");
    }

    function clearImagePreview() {
        setImagePreviewFile(null);
        setImagePreviewUrl("");
    }

    var chatEntries: any[] = notesData.data?.notesNotesList?.items?.toReversed();

    function handleChangeVisibility(visible: boolean) {
        if (!visible) { return; }
        if (notesData.loading || notesData.error) { return; }
        if (notesData.data.notesNotesList.page >= notesData.data.notesNotesList.maxPage) { return; }
        notesData.fetchMore({
            variables: {
                collectionId: props.collection.id,
                archived: "ALL",
                pages: {
                    page: notesData.data.notesNotesList.page + 1,
                    sort: ["-created_at_utc"]
                }
            },
        });
    };
    
    return <div>
        <div>
            {
                (notesData.loading) ? (
                    <Loading/>
                ) : (notesData.error) ? (
                    <span style={{color: "red"}}>
                        {t("notes.collection.error", {error: notesData.error.message})}
                    </span>
                ) : (chatEntries.length == 0) ? (
                    <span>
                        {t("notes.view.chat.empty")}
                    </span>
                ) : (
                    <div
                        style={{maxHeight: "50vh", overflow: "scroll"}}
                        ref={container}
                    >
                        <VisibilityObserver onChangeVisibility={handleChangeVisibility}/>
                        {
                            chatEntries.map((note: any) => {
                                return <Entry key={note.id} note={note}/>;
                            })
                        }
                    </div>
                )
            }
        </div>
        <form onSubmit={saveNote}>
            {
                imagePreviewUrl &&
                <div style={{position: "relative", maxWidth: "10rem", maxHeight: "10rem"}}>
                    <img
                        src={imagePreviewUrl}
                        style={{width: "100%", height: "100%"}}
                    />
                    <button
                        onClick={() => clearImagePreview()}
                        style={{position: "absolute", top: "0", right: "0"}}
                    >
                        X
                    </button>
                </div>
            }
            <input
                type="text"
                placeholder={t("notes.view.chat.new.placeholder")}
                value={newNoteContent}
                onChange={(e) => setNewNoteContent(e.target.value)}
            />
            <button type="submit">{t("notes.view.chat.new.button")}</button>
            <label htmlFor="file-upload">📸</label>
            <input
                type="file"
                accept="image/*"
                onChange={(e) => {
                    if (!e.target.files) { return; }
                    const firstFile = e.target.files[0];
                    setImagePreviewFile(firstFile);
                    setImagePreviewUrl(URL.createObjectURL(firstFile));
                }}

                id="file-upload"
                style={{display: "none"}}
            />
        </form>
    </div>;
}
