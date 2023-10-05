import React from 'react';
import { Link } from 'react-router-dom';
import Loading from '../../components/Loading';
import Pagination from '../../components/Pagination';
import { useTranslation } from 'react-i18next';
import { useActivityLogQuery } from './api';
import { GetRenderer, ParseRawActivity } from '../../components/Activity';

import ProfileRenderers from './activities';

const AllRenderers = {
    ...ProfileRenderers,
};

export default function Activity() {
    const { t } = useTranslation("common");
    const [page, setPage] = React.useState(0);
    const logVars = useActivityLogQuery(page);
    if (logVars.error) {
        return <span>
            {t("profile.login.title")} (<Link to="/">{t("profile.back_to_homepage")}</Link>)<br/>
            <span style={{color: "red"}}>{logVars.error.message}</span>
        </span>;
    } else if (logVars.loading) {
        return <span>
            {t("profile.login.title")} (<Link to="/">{t("profile.back_to_homepage")}</Link>)<br/>
            <Loading/>
        </span>;
    } else if (logVars.data) {
        return <>
            <div>
                {t("profile.login.title")} (<Link to="/">{t("profile.back_to_homepage")}</Link>)<br/>
            </div>
            <ol>
                {
                    logVars.data.profileActivityLog.items?.map((item: any) => {
                        const Renderer = GetRenderer(item, AllRenderers);
                        return <Renderer key={item.id} {...ParseRawActivity(item)} />;
                    })
                }
            </ol>
            <Pagination onSetPage={setPage} {...logVars.data.profileActivityLog}/>
        </>;
    } else {
        return <span>{t("profile.login.title")}</span>;
    }
}
