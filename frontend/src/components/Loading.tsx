import React from 'react';
import { useTranslation } from 'react-i18next';

export default function Loading() {
    const { t } = useTranslation("common");
    return <span>{t("loading")}</span>;
}
