import React from 'react';
import { useTranslation } from 'react-i18next';

export default function NotFound() {
    const { t } = useTranslation("common");
    return <span>{t("404_not_found")}</span>;
}
