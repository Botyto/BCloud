import React, { createRef, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import fspath from '../../fspath';
import { BROWSER_ROUTE } from '../common';
import MimeTypeIcon from '../MimeTypeIcon';
import Picker from '../../picker/Picker';

interface FileEntryHeaderProps {
    allSelected: boolean;
    partlySelected: boolean;
    toggleSelectAllPaths: () => void;
    onMove: () => void;
    onCopy: () => void;
    onDelete: () => void;
}

export function FileEntryHeader(props: FileEntryHeaderProps) {
    const { t } = useTranslation("common");
    const anySelected = props.allSelected || props.partlySelected;

    function onMove(e: React.MouseEvent) {
        e.preventDefault();
        props.onMove();
    }

    function onCopy(e: React.MouseEvent) {
        e.preventDefault();
        props.onCopy();
    }

    function onDelete(e: React.MouseEvent) {
        e.preventDefault();
        props.onDelete();
    }

    return <>
        <input
            type="checkbox"
            checked={props.allSelected}
            onChange={props.toggleSelectAllPaths}
            ref={input => {
                if (!input) { return; }
                input.indeterminate = props.partlySelected;
            }}
        />
        <span>
            <span style={{ display: "inline-block", minWidth: "2rem" }}></span>
            <span style={{ display: "inline-block", minWidth: "15rem" }}></span>
            <span style={{ display: "inline-block", minWidth: "5rem" }}></span>
            <button style={{ minWidth: "5rem" }} onClick={onMove} disabled={!anySelected}>{t("files.browser.dir.all.move")}</button>
            <button style={{ minWidth: "5rem" }} onClick={onCopy} disabled={!anySelected}>{t("files.browser.dir.all.copy")}</button>
            <button style={{ minWidth: "5rem" }} onClick={onDelete} disabled={!anySelected}>{t("files.browser.dir.all.delete.button")}</button>
        </span>
    </>
}

interface FileEntryProps {
    path: string;
    file: any;
    selected: boolean;
    onSelect: (selected: boolean) => void;
    onRename: () => void;
    onMove: () => void;
    onCopy: () => void;
    onDelete: () => void;
    onShare: () => void;
    onAddLink: () => void;
}

export function FileEntry(props: FileEntryProps) {
    const { t } = useTranslation("common");
    
    function onRename(e: React.MouseEvent) {
        e.preventDefault();
        props.onRename();
    }
    
    function onMove(e: React.MouseEvent) {
        e.preventDefault();
        props.onMove();
    }

    function onCopy(e: React.MouseEvent) {
        e.preventDefault();
        props.onCopy();
    }

    function onDelete(e: React.MouseEvent) {
        e.preventDefault();
        props.onDelete();
    }

    function onShare(e: React.MouseEvent) {
        e.preventDefault();
        props.onShare();
    }

    function onAddLink(e: React.MouseEvent) {
        e.preventDefault();
        props.onAddLink();
    }


    return <li style={{ border: "solid 1px black" }}>
        <input
            type="checkbox"
            checked={props.selected}
            onChange={e => props.onSelect(e.target.checked)}
        />
        <span style={{display: "inline-block", minWidth: "2rem"}}>
            <MimeTypeIcon type={props.file.type} mimeType={props.file.mimeType} />
        </span>
        <span style={{display: "inline-block", minWidth: "15rem"}}>
            <Link to={fspath.pathToUrl(BROWSER_ROUTE, props.path)}>
                {props.file.name}
            </Link>
        </span>
        <span>
            <button style={{ minWidth: "5rem" }} onClick={onRename}>{t("files.browser.dir.file.rename.button")}</button>
            <button style={{ minWidth: "5rem" }} onClick={onMove}>{t("files.browser.dir.file.move")}</button>
            <button style={{ minWidth: "5rem" }} onClick={onCopy}>{t("files.browser.dir.file.copy")}</button>
            <button style={{ minWidth: "5rem" }} onClick={onDelete}>{t("files.browser.dir.file.delete.button")}</button>
            <button style={{ minWidth: "5rem" }} onClick={onShare}>{t("files.browser.dir.file.share")}</button>
            <button style={{ minWidth: "5rem" }} onClick={onAddLink}>{t("files.browser.dir.file.link")}</button>
        </span>
    </li>;
}
