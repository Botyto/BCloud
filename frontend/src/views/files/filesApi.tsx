import { gql, useQuery } from '@apollo/client';

const FILES_LIST = gql`
query StorageList($path: String!) {
    filesFilesByPath(path: $path, followLastLink: false) {
        id
        name
        mimeType
        size
        atimeUtc
        mtimeUtc
        ctimeUtc
        type
        isroot
        totalSize
        children { 
            id
            name
            mimeType
            size
            atimeUtc
            mtimeUtc
            ctimeUtc
            type
            isroot
            totalSize
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
