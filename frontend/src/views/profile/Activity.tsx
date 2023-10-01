import React from 'react';
import { Link } from 'react-router-dom';
import Loading from '../../components/Loading';
import Pagination from '../../components/Pagination';
import { useActivityLogQuery } from './api';

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
                        const d = new Date();
                        d.setTime(Date.parse(item.createdAtUtc));
                        return <li key={item.id}>
                            <div>{d.toLocaleString()} {item.issuer} -&gt; {item.type}</div>
                            <div>{item.payload}</div>
                        </li>;
                    })
                }
            </ol>
            <Pagination onSetPage={setPage} {...logVars.data.profileActivityLog}/>
        </>;
    } else {
        return <span>Activity</span>;
    }
}
