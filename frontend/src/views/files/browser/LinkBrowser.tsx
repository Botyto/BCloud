import React from 'react';
import { useTranslation } from 'react-i18next';
import { ContentsProps } from './common';

export default function LinkBrowser(props: ContentsProps) {
    const { t } = useTranslation("common");
    return <span>{t("files.browser.link.follow")}</span>
}
