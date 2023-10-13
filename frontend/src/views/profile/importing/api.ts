import { gql, useMutation, useQuery, useApolloClient, ApolloClient } from '@apollo/client';

const RUNNING_IMPORTS = gql`
query RunningImports {
    profileImportingRunning {
        jobs
    }
}`;

export function useRunningImportsQuery() {
    return useQuery(RUNNING_IMPORTS);
}

export function refetchRunningImportsQuery(client: ApolloClient<object>) {
    client.refetchQueries({
        include: [RUNNING_IMPORTS]
    });
}

const GOOGLE_OPTIONS = gql`
query ImportGoogleOptions {
    profileImportingGoogleOptions {
        options
    }
}`;

export function useImportGoogleOptionsQuery() {
    return useQuery(GOOGLE_OPTIONS);
}

const GOOGLE_INIT = gql`
mutation ImportGoogleInit($options: [String]!) {
    profileImportingGoogleInit(options: $options) {
        url
    }
}`;

export function useImportGoogleInitMutation() {
    return useMutation(GOOGLE_INIT);
}
