import React from 'react';
import { useTranslation } from 'react-i18next';
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
    const { t } = useTranslation('common')
    const currentUserVars = useQuery(USER);
    if (currentUserVars.error) {
        return <span>{t('homepage.hi')} <span style={{color: "red"}}>{currentUserVars.error.message}</span></span>;
    } else if (currentUserVars.loading) {
        return <span>{t('homepage.hi')} <Loading/></span>
    } else if (currentUserVars.data) {
        const user = currentUserVars.data.profileAuthUser?.displayName || "MISSING USER";
        return <>
            <div>{t('homepage.hi_user', { user })}</div>
            <ul>
                <li>/profile</li>
                <li><Link to="/profile/login">/profile/login</Link></li>
                <li><Link to="/profile/activity">/profile/activity</Link></li>
                <li><Link to="/profile/import">/profile/import</Link></li>
                <li><Link to="/files">/files</Link></li>
                <li><Link to="/notes">/notes</Link></li>
            </ul>
        </>;
    } else {
        return <span>{t('homepage.hi')}</span>;
    }
}
