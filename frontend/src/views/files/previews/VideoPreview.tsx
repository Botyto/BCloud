import React from 'react';
import { useTranslation } from 'react-i18next';
import { PreviewProps, Preview, primaryMimeType } from './preview';

function VideoPreview(props: PreviewProps) {
    const { t } = useTranslation("common");

    return (
        <video>
            <source
                src={props.contentUrl}
                type={props.file.mimeType}
            />
            <span style={{color: "red"}}>{t("files.browser.file.preview.video_not_supported")}</span>
        </video>
    );
}

export default new Preview(primaryMimeType("video/"), VideoPreview, true);
