import React from 'react';
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
            <button style={{minWidth: "5rem"}} disabled>Move</button>
            <button style={{minWidth: "5rem"}} disabled>Copy</button>
            <button style={{minWidth: "5rem"}} disabled>Delete</button>
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
            <button style={{minWidth: "5rem"}} disabled>Rename</button>
            <button style={{minWidth: "5rem"}} disabled>Move</button>
            <button style={{minWidth: "5rem"}} disabled>Copy</button>
            <button style={{minWidth: "5rem"}} disabled>Delete</button>
            <button style={{minWidth: "5rem"}} disabled>Share</button>
            <button style={{minWidth: "5rem"}} disabled>Follow link</button>
            <button style={{minWidth: "5rem"}} disabled>Add link</button>
            <button style={{minWidth: "5rem"}} disabled>Transcode</button>
        </span>
    </li>;
}
