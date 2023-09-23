import React, { useState } from 'react';
import { gql, useQuery } from '@apollo/client';

const USER = gql`
query CurrentUser {
    profileAuthUser {
        displayName
    }
}`

export default function Homepage() {
    const currentUserVars = useQuery(USER);
    if (currentUserVars.error) {
        return <span>Hi <span style={{color: "red"}}>{currentUserVars.error.message}</span></span>;
    } else if (currentUserVars.data) {
        return <span>Hi {currentUserVars.data.profileAuthUser?.displayName || "MISSING USER"}</span>;
    } else {
        return <span>Hi</span>;
    }
}
