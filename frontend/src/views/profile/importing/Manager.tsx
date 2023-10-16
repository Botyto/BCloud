import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Loading from '../../../components/Loading';
import { useRunningImportsQuery } from './api';

export default function Importing() {
    const { t } = useTranslation("common");
    const runningVars = useRunningImportsQuery();

    const header = <span>{t("profile.importing.title")} (<Link to="/">{t("profile.back_to_homepage")}</Link>)</span>;
    var running;

    if (runningVars.error) {
        running = <span style={{ color: "red" }}>{runningVars.error.message}</span>;
    } else if (runningVars.loading) {
        running = <Loading />;
    } else {
        running = <div>
            {t("profile.importing.running")}:
            {
                (runningVars.data.profileImportingRunning.jobs.length === 0) ? (
                    <>{t("profile.importing.no_running")}</>
                ) : (
                    <ul>
                        {
                            runningVars.data.profileImportingRunning.jobs.map((job: string) => {
                                return <li key={job}>{t(`profile.${job}.name`)}</li>;
                            })
                        }
                    </ul>
                )
            }
        </div>;
    }

    return <>
        <div>{header}</div>
        <div>{running}</div>
        <div>
            {t("profile.importing.begin")}:<br/>
            <Link to="/profile/import/google">{t("profile.importing.google.name")}</Link><br/>
        </div>
    </>;
}
