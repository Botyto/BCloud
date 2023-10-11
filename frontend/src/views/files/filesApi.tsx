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

const FILES_COPY = gql`
${FILE_DETAILS}
mutation filesCopy($src: String!, $dst: String!) {
    filesFilesCopyfile(src: $src, dst: $dst) {
        ...FileDetails
    }
}`;

export function useFilesCopyMutation() {
    return useMutation(FILES_COPY, {
        refetchQueries: [FILES_LIST],
    });
}

const FILES_RENAME = gql`
${FILE_DETAILS}
mutation filesRename($src: String!, $dst: String!) {
    filesFilesRename(src: $src, dst: $dst) {
        ...FileDetails
    }
}`;

export function useFilesRenameMutation() {
    return useMutation(FILES_RENAME, {
        refetchQueries: [FILES_LIST],
    });
}

const FILES_DELETE = gql`
mutation filesDelete($path: String!) {
    filesFilesDelete(path: $path) {
        success
    }
}`;

export function useFileDeleteMutation() {
    return useMutation(FILES_DELETE, {
        refetchQueries: [FILES_LIST],
    });
}

const FILES_LINK = gql`
${FILE_DETAILS}
mutation filesLink($path: String!, $target: String!) {
    filesFilesMakelink(path: $path, target: $target) {
        ...FileDetails
    }
}`;

export function useFileLinkMutation() {
    return useMutation(FILES_LINK, {
        refetchQueries: [FILES_LIST],
    });
}

