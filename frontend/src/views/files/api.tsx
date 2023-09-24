import { gql, useQuery, useMutation } from '@apollo/client';

const STORAGE_LIST = gql`
query StorageList($pages: InputPagesInput!) {
    filesStorageList(pages: $pages) {
        total
        page
        maxPage
        items {
            id
            name
        }
    }
}`;

export function useStorageListQuery(page: number) {
    return useQuery(STORAGE_LIST, {
        variables: {
            pages: {
                page: page,
            },
        },
    });
}

const STORAGE_META = gql`
query StorageMeta($id: ID!) {
    filesStorageMetadata(id: $id) {
        id
        name
    }
}`;

export function useStorageMetaQuery(id: string) {
    return useQuery(STORAGE_META, {
        variables: {
            id,
        },
    });
}

const STORAGE_CREATE = gql`
mutation StorageCreate($name: String!) {
    filesStorageCreate(name: $name) {
        id
        name
    }
}`

export function useStorageCreateMutation() {
    return useMutation(STORAGE_CREATE);
}
