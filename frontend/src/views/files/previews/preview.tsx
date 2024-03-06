import React from 'react';
import { useTranslation } from 'react-i18next';

export interface PreviewProps {
    file: any;
    path: string;
    contentUrl: string;
    editing: boolean;
}

export class Preview {
    filter: (mimeType: string) => boolean;
    component: React.FC<PreviewProps>;
    hasPreview: boolean;
    canEdit: boolean;

    constructor(
        filter: (mimeType: string) => boolean,
        component: React.FC<PreviewProps>,
        hasPreview: boolean = true,
        canEdit: boolean = false,
    ) {
        this.filter = filter;
        this.component = component;
        this.hasPreview = hasPreview;
        this.canEdit = canEdit;
    }
}


function FallbackPreview(props: PreviewProps) {
    const { t } = useTranslation("common");
    return <div>{t("files.browser.file.preview.unknown_file_type")}</div>;
}
const FallbackPreviewMeta = new Preview(() => true, FallbackPreview, false, false);


export function GetPreviewMeta(file: any, previews: Preview[]) {
    for (const preview of previews) {
        if (preview.filter(file.mimeType)) {
            return preview;
        }
    }
    return FallbackPreviewMeta;
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

export function listMimeType(mimeTypes: string[]) {
    return function(inputMimeType: string) {
        return mimeTypes.includes(inputMimeType);
    }
}
