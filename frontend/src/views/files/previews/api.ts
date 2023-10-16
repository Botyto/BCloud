import { gql, useQuery } from '@apollo/client';

const PREVIEW_ARCHIVE = gql`
query ArchivePreview($path: String!) {
    filesPreviewArchive(path: $path) {
        files {
            path
            mime
        }
    }
}`;

export function useArchivePreviewQuery(path: string) {
    return useQuery(PREVIEW_ARCHIVE, {
        variables: {
            path,
        },
    });
}
