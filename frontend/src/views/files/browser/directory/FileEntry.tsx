import React from 'react';
import { Link } from 'react-router-dom';
import fspath from '../../fspath';
import { BROWSER_ROUTE } from '../common';
import MimeTypeIcon from '../MimeTypeIcon';

interface FileEntryProps {
    path: string;
    file: any;
    selected: boolean;
    onSelect: (selected: boolean) => void;
}

export default function FileEntry(props: FileEntryProps) {
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
            <button disabled>Rename</button>
            <button disabled>Move</button>
            <button disabled>Copy</button>
            <button disabled>Delete</button>
            <button disabled>Share</button>
            <button disabled>Follow link</button>
            <button disabled>Add link</button>
            <button disabled>Transcode</button>
        </span>
    </li>;
}
