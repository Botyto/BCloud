import React from 'react';
import { gql, useQuery } from '@apollo/client';
import { Link } from 'react-router-dom';
import Loading from '../components/Loading';

const USER = gql`
query CurrentUser {
    profileAuthUser {
        id
        displayName
    }
}`;

export default function Homepage() {
    const currentUserVars = useQuery(USER);
    if (currentUserVars.error) {
        return <span>Hi <span style={{color: "red"}}>{currentUserVars.error.message}</span></span>;
    } else if (currentUserVars.loading) {
        return <span>Hi <Loading/></span>
    } else if (currentUserVars.data) {
        return <>
            <div>Hi {currentUserVars.data.profileAuthUser?.displayName || "MISSING USER"}</div>
            <ul>
                <li>/profile</li>
                <li><Link to="/profile/login">/profile/login</Link></li>
                <li><Link to="/profile/activity">/profile/activity</Link></li>
                <li><Link to="/files">/files</Link></li>
            </ul>
        </>;
    } else {
        return <span>Hi</span>;
    }
}
