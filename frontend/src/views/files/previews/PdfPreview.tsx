import React from 'react';
import { PreviewProps, Preview, exactMimeType } from './preview';

function PdfPreview(props: PreviewProps) {
    return <embed
        src={props.contentUrl}
        style={{width: '100%', height: '88vh'}}
        type={props.file.mimeType}
        // frameBorder="0"
        // scrolling="auto"
    />;
}

export default new Preview(exactMimeType("application/pdf"), PdfPreview, true);
