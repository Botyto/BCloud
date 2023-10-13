import { gql, useMutation, useQuery } from '@apollo/client';

const AUTH_LOGIN = gql`
mutation AuthLogin($username: String!, $password: String!) {
    profileAuthLogin(username: $username, password: $password) {
        jwt
    }
}`;

export function useLoginMutation() {
    return useMutation(AUTH_LOGIN);
}

const AUTH_REGISTER = gql`
mutation AuthRegister($username: String!, $password: String!) {
    profileAuthRegister(username: $username, password: $password) {
        jwt
    }
}`;

export function useRegisterMutation() {
    return useMutation(AUTH_REGISTER);
}

const ACTIVITY_LOG = gql`
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

export function useActivityLogQuery(page: number) {
    return useQuery(ACTIVITY_LOG, {
        variables: {
            pages: {
                page: page,
            },
        },
    });
}
