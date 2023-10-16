import React from 'react';
import { PreviewProps, Preview, primaryMimeType } from './preview';

function ImagePreview(props: PreviewProps) {
    return <img
        src={props.contentUrl}
        alt={props.file.name}
        style={{ maxWidth: "100vw", maxHeight: "90vh" }}
    />;
}

export default new Preview(primaryMimeType("image/"), ImagePreview, true);
