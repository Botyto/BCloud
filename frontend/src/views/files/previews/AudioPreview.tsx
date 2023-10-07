import React from 'react';
import { useTranslation } from 'react-i18next';
import { PreviewProps, Preview, primaryMimeType } from './preview';

function AudioPreview(props: PreviewProps) {
    const { t } = useTranslation("common");

    return (
        <audio controls>
            <source
                src={props.contentUrl}
                type={props.file.mime_type}
            />
            <span style={{color: "red"}}>{t("files.browser.file.preview.audio_not_supported")}</span>
        </audio>
    );
}

export default new Preview(primaryMimeType("audio"), AudioPreview, true);
