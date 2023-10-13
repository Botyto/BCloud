import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Loading from '../../../components/Loading';
import { useImportGoogleOptionsQuery, useRunningImportsQuery } from '../api';

export default function Google() {
    const { t } = useTranslation("common");
    const runningVars = useRunningImportsQuery();
    const optionsVars = useImportGoogleOptionsQuery();
    const [useOptions, setUseOptions] = React.useState<string[] | null>(null);
    
    function setUseOption(option: string, value: boolean) {
        if (useOptions === null) { return; }
        if (value) {
            setUseOptions([...useOptions, option]);
        } else {
            setUseOptions(useOptions.filter((v) => v !== option));
        }
    }

    const header = <span>
        {t("profile.importing.google.name")}
        (<Link to="/profile/import">{t("profile.back_to_importing")}</Link>)
    </span>;

    var running = null;
    if (runningVars.error) {
        running = <span style={{ color: "red" }}>{runningVars.error.message}</span>;
    } else if (runningVars.loading) {
        running = <Loading />;
    } else if (runningVars.data.profileImportingRunning.jobs.includes("importing.google")) {
        running = <div>{t("profile.importing.is_running")}</div>;
    }

    var options;
    if (optionsVars.error) {
        options = <span style={{ color: "red" }}>{optionsVars.error.message}</span>;
    } else if (optionsVars.loading) {
        options = <Loading />;
    } else {
        if (useOptions === null) {
            setUseOptions(optionsVars.data.profileImportingGoogleOptions.options);
        }
        options = <div>
            {
                optionsVars.data.profileImportingGoogleOptions.options.map((option: string) => {
                    return <div key={option}>
                        <input
                            type="checkbox"
                            checked={useOptions?.includes(option)}
                            onChange={(e) => setUseOption(option, e.target.checked)}
                        />
                        {t("profile.importing.google.opts." + option)}
                    </div>;
                })
            }
        </div>
    }

    return <>
        <div>{header}</div>
        {
            running || <>
                {t("profile.importing.google.description")}
                {options}
                <button disabled={useOptions?.length === 0}>{t("profile.importing.run")}</button>
            </>
        }
    </>;
}
