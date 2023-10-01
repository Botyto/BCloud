import React from 'react';
import { Link } from 'react-router-dom';
import Loading from '../../components/Loading';
import Pagination from '../../components/Pagination';
import { useActivityLogQuery } from './api';
import { GetRenderer, ParseRawActivity } from '../../components/Activity';

import ProfileRenderers from './activities';

const AllRenderers = {
    ...ProfileRenderers,
};

export default function Activity() {
    const [page, setPage] = React.useState(0);
    const logVars = useActivityLogQuery(page);
    if (logVars.error) {
        return <span>
            Activity (<Link to="/">homepage</Link>)<br/>
            <span style={{color: "red"}}>{logVars.error.message}</span>
        </span>;
    } else if (logVars.loading) {
        return <span>
            Activity (<Link to="/">homepage</Link>)<br/>
            <Loading/>
        </span>;
    } else if (logVars.data) {
        return <>
            <div>
                Activity (<Link to="/">homepage</Link>)
            </div>
            <ol>
                {
                    logVars.data.profileActivityLog.items?.map((item: any) => {
                        const Renderer = GetRenderer(item, AllRenderers);
                        return Renderer(ParseRawActivity(item));
                    })
                }
            </ol>
            <Pagination onSetPage={setPage} {...logVars.data.profileActivityLog}/>
        </>;
    } else {
        return <span>Activity</span>;
    }
}
