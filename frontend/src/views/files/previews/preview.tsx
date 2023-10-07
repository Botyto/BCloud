import React from 'react';
import { useTranslation } from 'react-i18next';

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
    const { t } = useTranslation("common");
    return <div>{t("files.browser.file.preview.unknown_file_type")}</div>;
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

export function primaryMimeType(mimeType: string) {
    return function(inputMimeType: string) {
        return inputMimeType.startsWith(mimeType);
    };
}
