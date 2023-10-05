import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import fspath from '../../fspath';
import { BROWSER_ROUTE } from '../common';
import MimeTypeIcon from '../MimeTypeIcon';

interface FileEntryHeaderProps {
    allSelected: boolean;
    partlySelected: boolean;
    toggleSelectAllPaths: () => void;
}

export function FileEntryHeader(props: FileEntryHeaderProps) {
    const { t } = useTranslation("common");
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
            <button style={{ minWidth: "5rem" }} disabled>{t("files.browser.dir.all.move")}</button>
            <button style={{ minWidth: "5rem" }} disabled>{t("files.browser.dir.all.copy")}</button>
            <button style={{ minWidth: "5rem" }} disabled>{t("files.browser.dir.all.delete")}</button>
        </span>
    </>
}

interface FileEntryProps {
    path: string;
    file: any;
    selected: boolean;
    onSelect: (selected: boolean) => void;
}

export function FileEntry(props: FileEntryProps) {
    const { t } = useTranslation("common");
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
            <button style={{ minWidth: "5rem" }} disabled>{t("files.browser.dir.file.rename")}</button>
            <button style={{ minWidth: "5rem" }} disabled>{t("files.browser.dir.file.move")}</button>
            <button style={{ minWidth: "5rem" }} disabled>{t("files.browser.dir.file.copy")}</button>
            <button style={{ minWidth: "5rem" }} disabled>{t("files.browser.dir.file.delete")}</button>
            <button style={{ minWidth: "5rem" }} disabled>{t("files.browser.dir.file.share")}</button>
            <button style={{ minWidth: "5rem" }} disabled>{t("files.browser.dir.file.follow")}</button>
            <button style={{ minWidth: "5rem" }} disabled>{t("files.browser.dir.file.link")}</button>
            <button style={{ minWidth: "5rem" }} disabled>{t("files.browser.dir.file.transcode")}</button>
        </span>
    </li>;
}
