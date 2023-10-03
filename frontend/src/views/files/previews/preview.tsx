import React from 'react';

export interface PreviewProps {
    file: any;
    path: string;
    contentUrl: string;
}

export class Preview {
    filter: (mimeType: string) => boolean;
    component: React.FC<PreviewProps>;
    hasPreview: boolean;

    constructor(filter: (mimeType: string) => boolean, component: React.FC<PreviewProps>, hasPreview: boolean = true) {
        this.filter = filter;
        this.component = component;
        this.hasPreview = hasPreview;
    }
}

function FallbackPreview(props: PreviewProps) {
    return <div>Unknown file type</div>;
}

export function GetPreview(file: any, previews: Preview[]) {
    for (const preview of previews) {
        if (preview.filter(file.mimeType)) {
            return preview.component;
        }
    }
    return FallbackPreview;
}

export function exactMimeType(mimeType: string) {
    return function(inputMimeType: string) {
        return inputMimeType == mimeType;
    };
}
