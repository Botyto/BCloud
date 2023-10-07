import React from 'react';
import { PreviewProps, Preview, primaryMimeType } from './preview';

function ImagePreview(props: PreviewProps) {
    return <img
        src={props.contentUrl}
        alt={props.file.name}
    />;
}

export default new Preview(primaryMimeType("image/"), ImagePreview, true);
