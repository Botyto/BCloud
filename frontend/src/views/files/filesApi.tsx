import { gql, useQuery, useMutation } from '@apollo/client';

const FILE_DETAILS = gql`
fragment FileDetails on FileMetadata {
    id
    name
    mimeType
    size
    atimeUtc
    mtimeUtc
    ctimeUtc
    type
    totalSize
}`;

const FILES_LIST = gql`
${FILE_DETAILS}
query FilesList($path: String!) {
    filesFilesByPath(path: $path, followLastLink: false) {
        ...FileDetails
        children { 
           ...FileDetails
        }
    }
}`;

export function useFilesListQuery(path: string) {
    return useQuery(FILES_LIST, {
        variables: {
            path,
        },
    });
}

const FILES_MAKEFILE = gql`
${FILE_DETAILS}
mutation filesMakefile($path: String!, $mimeType: String!) {
    filesFilesMakefile(path: $path, mimeType: $mimeType) {
        ...FileDetails
    }
}`;

export function useFilesMakefileMutation() {
    return useMutation(FILES_MAKEFILE, {
        refetchQueries: [FILES_LIST],
    });
}

const FILES_MAKEDIRS = gql`
${FILE_DETAILS}
mutation filesMakedirs($path: String!) {
    filesFilesMakedirs(path: $path) {
        ...FileDetails
    }
}`;

export function useFilesMakedirsMutation() {
    return useMutation(FILES_MAKEDIRS, {
        refetchQueries: [FILES_LIST],
    });
}
