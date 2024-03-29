import React, { useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useImportGoogleOptionsQuery, useRunningImportsQuery, useImportGoogleInitMutation, useImportGoogleStartMutation } from './api';
import Loading from '../../../components/Loading';

export function Google() {
    const { t } = useTranslation("common");
    const runningVars = useRunningImportsQuery();
    const optionsVars = useImportGoogleOptionsQuery();
    const [useOptions, setUseOptions] = React.useState<string[] | null>(null);
    const [init, initVars] = useImportGoogleInitMutation();
    const [err, setErr] = React.useState<string | null>(null);
    
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

    function onRun(e: React.MouseEvent) {
        e.preventDefault();
        init({
            variables: {
                options: useOptions,
            },
            onCompleted: (data) => {
                window.location.href = data.profileImportingGoogleInit.url;
            },
            onError: (error) => {
                setErr(error.message);
            },
        })
    }

    return <>
        <div>{header}</div>
        {
            running || <>
                {t("profile.importing.google.description")}
                {options}
                <button
                    disabled={useOptions?.length === 0}
                    onClick={onRun}
                >
                    {t("profile.importing.run")}
                </button>
                <div style={{ color: "red" }}>{err}</div>
            </>
        }
    </>;
}

export function GoogleCallback(props: any) {
    const [params, _] = useSearchParams();
    const navigate = useNavigate();
    const code = params.get("code");
    const state = params.get("state");
    const scope = params.get("scope");
    const { t } = useTranslation("common");
    const [googleStart, googleStartVars] = useImportGoogleStartMutation();

    useEffect(() => {
        googleStart({
            variables: {
                code,
                state,
                scope,
            },
            onCompleted: (data) => {
                navigate("/profile/import");
            },
        });
    }, []);

    if (googleStartVars.error !== undefined) {
        return <>
            <div>(<Link to="/profile/import">{t("profile.back_to_importing")}</Link>)</div>
            <div style={{ color: "red" }}>{googleStartVars.error.message}</div>
        </>;
    } else {
        return <Loading/>;
    }
}
