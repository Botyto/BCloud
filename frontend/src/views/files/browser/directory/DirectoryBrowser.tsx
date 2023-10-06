import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import fspath from '../../fspath';
import { ContentsProps } from '../common';
import { FileEntryHeader, FileEntry } from './FileEntry';
import DirControls from './DirControls';
import { Dialog, bindState, useDialogState } from '../../../../components/Dialog';
import Picker from '../../picker/Picker';

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

    const allSelected = selectedPaths.length === props.file.children.length;
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
        showTypes: string[]|undefined = undefined,
    ) {
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
    
    // Actions

    function onRename(path: string) {
        const originalName = fspath.baseName(path);
        const name = prompt(t("files.browser.dir.file.rename.prompt", {name: originalName}), originalName);
        if (!name || name === originalName) { return; }
        console.log("Will rename", path, "to", name);
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
        console.log("Will move");
        console.log(src);
        console.log("To", dst);
        setPickerFiles([]);
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

    function doCopy(src: string[], dst: string) {
        if (dst === props.path) { return; }
        console.log("Will copy");
        console.log(src);
        console.log("To", dst);
    }

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
        console.log("Will delete");
        console.log(paths);
    }

    function onShare(path: string) {
        alert("Not implemented!");
    }

    function onAddLink(path: string) {
        openPicker(
            [path],
            t("files.browser.dir.file.link.prompt"),
            t("files.browser.dir.file.link.action"),
            doLink,
            t("files.browser.dir.file.link.input_label"),
            "Link to " + fspath.baseName(path),
            ["DIRECTORY"],
        );
    }

    function doLink(src: string[], path: string) {
        const linkedFile = src[0];
        console.log("Will link", linkedFile, "to", path);
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
            />
        </Dialog>
        <DirControls path={props.path} />
    </>;
}
