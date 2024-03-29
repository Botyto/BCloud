import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import fspath from '../../fspath';
import { ContentsProps } from '../common';
import { FileEntryHeader, FileEntry } from './FileEntry';
import DirControls from './DirControls';
import { Dialog, bindState, useDialogState } from '../../../../components/Dialog';
import Picker from '../../picker/Picker';
import { useFilesCopyMutation, useFilesRenameMutation, useFileDeleteMutation, useFileLinkMutation, useFileSetAccessMutation } from '../../filesApi';

export default function DirectoryContents(props: ContentsProps) {
    const { t } = useTranslation("common");

    // Selection

    const [selectedPaths, setSelectedPaths] = React.useState<string[]>([]);

    function setPathSelected(path: string, selected: boolean) {
        if (selected && !selectedPaths.includes(path)) {
            setSelectedPaths([...selectedPaths, path]);
        } else if (!selected && selectedPaths.includes(path)) {
            setSelectedPaths(selectedPaths.filter(p => p !== path));
        }
    }

    function isSelected(path: string) {
        return selectedPaths.includes(path);
    }

    const numFiles = props.file.children.length;
    const allSelected = numFiles > 0 && selectedPaths.length === numFiles;
    const partlySelected = selectedPaths.length > 0 && !allSelected;
    function toggleSelectAllPaths() {
        if (allSelected) {
            setSelectedPaths([]);
        } else if (props.file.children) {
            setSelectedPaths(props.file.children.map(
                (file: any) => fspath.join(null, [props.path, file.name])
            ));
        }
    }

    // Picker

    const [pickerFiles, setPickerFiles] = useState<string[]>([]);
    const [pickerTitle, setPickerTitle] = useState<string>("");
    const [pickerActionName, setPickerActionName] = useState<string>("");
    const [pickerAction, setPickerAction] = useState<((src: string[], dst: string)=>void)>(()=>{});
    const [pickerInputLabel, setPickerInputLabel] = useState<string>("");
    const [pickerInputDefault, setPickerInputDefault] = useState<string>("");
    const [pickerShowTypes, setPickerShowTypes] = useState<string[]|undefined>(undefined);
    const picker = useDialogState();
    
    function openPicker(
        paths: string[],
        title: string,
        actionName: string,
        action: (src: string[], dst: string)=>void,
        inputLabel: string = "",
        inputDefault: string = "",
        showTypes: string[]|undefined = undefined)
    {
        setPickerFiles(paths);
        setPickerTitle(title);
        setPickerActionName(actionName);
        setPickerAction(() => action);
        setPickerInputLabel(inputLabel);
        setPickerInputDefault(inputDefault);
        setPickerShowTypes(showTypes);
        picker.open();
    }
    
    function resetPicker() {
        setPickerFiles([]);
        setPickerTitle("");
        setPickerActionName("");
        setPickerAction(()=>{});
        setPickerInputLabel("");
        setPickerInputDefault("");
        setPickerShowTypes(undefined);
    }

    // Share
    
    const [sharePath, setSharePath] = useState<string>("");
    const [shareAccess, setShareAccess] = useState<string>("");
    const share = useDialogState();
    
    // Actions
        
    const [renameFile, renameFileVars] = useFilesRenameMutation();
    const [renameTitle, setRenameTitle] = useState<string>("");
    const [renamePath, setRenamePath] = useState<string>("");
    const [renameName, setRenameName] = useState<string>("");
    const rename = useDialogState();
    function onRename(path: string) {
        setRenamePath(path);
        const originalName = fspath.baseName(path);
        setRenameName(originalName);
        setRenameTitle(t("files.browser.dir.file.rename.prompt", { name: originalName }));
        rename.open();
    }
    function doRename() {
        const originalName = fspath.baseName(renamePath);
        if (renameName == "" || renameName == originalName) {
            return;
        }
        const dst = fspath.join(null, [props.path, renameName]);
        renameFile({
            variables: { src: renamePath, dst },
            onCompleted: () => {
                setPathSelected(dst, isSelected(renamePath));
                setPathSelected(renamePath, false);
            },
            onError: (err) => { alert("Error:\n" + err); },
        });
        rename.close();
        setRenameName("");
        setRenamePath("");
        setRenameTitle("");
    }

    function onMove(paths: string[], single: boolean) {
        var title = "";
        if (single) {
            const name = fspath.baseName(paths[0]);
            title = t("files.browser.dir.file.move.prompt", { name });
        } else {
            const count = paths.length;
            title = t("files.browser.dir.all.move.prompt", { count });
        }
        openPicker(paths, title, t("files.browser.dir.file.move.action"), doMove, undefined, undefined, ["DIRECTORY"]);
    }

    function doMove(src: string[], dst: string) {
        if (dst === props.path) { return; }
        for (const fileSrc of src) {
            const fileDst = fspath.join(null, [dst, fspath.baseName(fileSrc)]);
            renameFile({
                variables: { src: fileSrc, dst: fileDst },
                onCompleted: () => { setPathSelected(fileSrc, false) },
                onError: (err) => { alert(fileSrc + " error:\n" + err); },
            });
        }
    }
    
    function onCopy(paths: string[], single: boolean) {
        var title = "";
        if (single) {
            const name = fspath.baseName(paths[0]);
            title = t("files.browser.dir.file.copy.prompt", { name });
        } else {
            const count = paths.length;
            title = t("files.browser.dir.all.copy.prompt", { count });
        }
        openPicker(paths, title, t("files.browser.dir.file.copy.action"), doCopy, undefined, undefined, ["DIRECTORY"]);
    }
    
    const [copyFile, copyFileVars] = useFilesCopyMutation();
    function doCopy(src: string[], dst: string) {
        if (dst === props.path) { return; }
        for (const fileSrc of src) {
            const fileDst = fspath.join(null, [dst, fspath.baseName(fileSrc)]);
            copyFile({
                variables: { src: fileSrc, dst: fileDst },
                onError: (err) => { alert(fileSrc + " error:\n" + err); },
            });
        }
    }

    const [deleteFile, deleteFileVars] = useFileDeleteMutation();
    function onDelete(paths: string[], single: boolean) {
        var title = "";
        if (single) {
            const name = fspath.baseName(paths[0]);
            title = t("files.browser.dir.file.delete.prompt", { name });
        } else {
            const count = paths.length;
            title = t("files.browser.dir.all.delete.prompt", { count });
        }
        const ok = window.confirm(title);
        if (!ok) { return; }
        for (const path of paths) {
            deleteFile({
                variables: { path },
                onCompleted: () => { setPathSelected(path, false); },
                onError: (err) => { alert("Error:\n" + err); },
            });
        }
    }

    function onShare(path: string) {
        setSharePath(path);
        const basename = fspath.baseName(path);
        const file = props.file.children.find((f: any) => f.name === basename);
        setShareAccess(file.access);
        share.open();
    }

    const [setAccess, setAccessVars] = useFileSetAccessMutation();
    function doShare(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        setAccess({
            variables: {
                path: sharePath,
                access: shareAccess,
            },
            onCompleted: () => {
                share.close();
            },
            onError: (e) => {
                alert("Error:\n" + e.message);
            },
        })
    }

    const [makeLink, makeLinkVars] = useFileLinkMutation();
    function onAddLink(path: string) {
        openPicker(
            [path],
            t("files.browser.dir.file.link.prompt", { name: fspath.baseName(path) }),
            t("files.browser.dir.file.link.action"),
            doLink,
            t("files.browser.dir.file.link.input_label"),
            "Link to " + fspath.baseName(path),
            ["DIRECTORY"],
        );
    }

    function doLink(src: string[], path: string) {
        const linkedFile = src[0];
        makeLink({
            variables: {
                path: path,
                target: linkedFile,
            },
            onError: (e) => { alert("Error:\n" + e.message); },
        });
    }

    // Render

    return <>
        <div>
            <div>
                <FileEntryHeader
                    allSelected={allSelected}
                    partlySelected={partlySelected}
                    toggleSelectAllPaths={toggleSelectAllPaths}
                    onMove={() => onMove(selectedPaths, false)}
                    onCopy={() => onCopy(selectedPaths, false)}
                    onDelete={() => onDelete(selectedPaths, false)}
                />
            </div>
            {
                (props.file.children.length === 0) ? (
                    <span>{t("files.browser.dir.empty")}</span>
                ) : (props.file.children.map((file: any) => {
                        const path = fspath.join(null, [props.path, file.name]);
                        return <FileEntry
                            file={file}
                            path={path}
                            selected={selectedPaths.includes(path)}
                            onSelect={(s) => setPathSelected(path, s)}
                            onRename={() => onRename(path)}
                            onMove={() => onMove([path], true)}
                            onCopy={() => onCopy([path], true)}
                            onDelete={() => onDelete([path], true)}
                            onShare={() => onShare(path)}
                            onAddLink={() => onAddLink(path)}
                            key={file.id}
                        />;
                    })
                )
            }
        </div>
        <Dialog {...bindState(rename)}>
            <div>{renameTitle}</div>
            <form onSubmit={doRename}>
                <input type="text" value={renameName} onChange={(e) => setRenameName(e.target.value)} />
                <input type="submit" value="Save"/>
            </form>
        </Dialog>
        <Dialog {...bindState(share)}>
            <form onSubmit={doShare}>
                <select value={shareAccess} onChange={(e) => setShareAccess(e.target.value)}>
                    <option value="SERVICE" disabled>Service</option>
                    <option value="HIDDEN">Hidden</option>
                    <option value="SECURE">Secured</option>
                    <option value="PRIVATE">Only you can see</option>
                    <option value="PUBLIC_READABLE">Everyone can see</option>
                    <option value="PUBLIC_WRITABLE">Everyone can edit</option>
                </select>
                <input type="submit" value="Save"/>
            </form>
        </Dialog>
        <Dialog {...bindState(picker)}>
            <Picker
                title={pickerTitle}
                defaultPath={props.path}
                actions={[{
                    name: pickerActionName,
                    onClick: (dst: string) => pickerAction(pickerFiles, dst),
                }]}
                onCancel={() => { picker.close(); resetPicker(); }}
                showTypes={pickerShowTypes}
                input={!!pickerInputLabel}
                inputLabel={pickerInputLabel}
                inputDefault={pickerInputDefault}
                disabledPaths={pickerFiles}
            />
        </Dialog>
        <DirControls path={props.path} />
    </>;
}
