import React from 'react';
import { gql, useQuery } from '@apollo/client';
import Loading from '../../components/Loading';
import Pagination from '../../components/Pagination';

const LOG = gql`
query ActivityLog($pages: InputPagesInput!) {
    profileActivityLog(pages: $pages) {
        total
        page
        maxPage
        items {
            id
            createdAtUtc
            issuer
            type
            payload
        }
    }
}`;

export default function Activity() {
    const [page, setPage] = React.useState(0);
    const logVars = useQuery(LOG, {
        variables: {
            pages: {
                page: page,
            },
        },
    });
    if (logVars.error) {
        return <span>Activity <span style={{color: "red"}}>{logVars.error.message}</span></span>;
    } else if (logVars.loading) {
        return <span>Activity <Loading/></span>
    } else if (logVars.data) {
        return <>
            <div>Activity</div>
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
