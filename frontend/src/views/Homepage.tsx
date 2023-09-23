import React from 'react';
import { gql, useQuery } from '@apollo/client';
import Loading from '../components/Loading';

const USER = gql`
query CurrentUser {
    profileAuthUser {
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
        return <span>Hi {currentUserVars.data.profileAuthUser?.displayName || "MISSING USER"}</span>;
    } else {
        return <span>Hi</span>;
    }
}
