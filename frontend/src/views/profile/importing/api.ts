import { gql, useMutation, useQuery } from '@apollo/client';

const RUNNING_IMPORTS = gql`
query RunningImports {
    profileImportingRunning {
        jobs
    }
}`;

export function useRunningImportsQuery() {
    return useQuery(RUNNING_IMPORTS);
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
