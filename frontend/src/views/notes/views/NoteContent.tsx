import React, { useRef, MutableRefObject } from 'react';
import ContentEditable, { ContentEditableEvent } from 'react-contenteditable';
import { mdToHtml, htmlToMd } from './Markdown';

interface NoteContentProps {
    editable?: boolean;
    content: MutableRefObject<string>;
}

export default function NoteContent(props: NoteContentProps) {
    const editor = useRef<HTMLDivElement>();
    const html = useRef(mdToHtml(props.content.current, true));

    function handleChange() {
        const htmlRoot: HTMLElement = editor.current.el.current;
        const md = htmlToMd(htmlRoot);
        props.content.current = md;
    };

    function handleBlur() {
        handleChange();
        html.current = mdToHtml(props.content.current, true);
    }
    
    return <ContentEditable
        ref={editor}
        html={html.current}
        onChange={handleChange}
        onBlur={handleBlur}
        disabled={!props.editable}
    />;
};
