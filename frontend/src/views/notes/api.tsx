import { gql, useMutation, useQuery } from '@apollo/client';

const COLLECTION_PROPS = gql`
fragment CollectionProps on NotesCollection {
    id
    name
    slug
    view
    archived
    access
}`;

const COLLECTIONS_TREE = gql`
${COLLECTION_PROPS}
query CollectionsTree($archived: InputEnumArchivedFilter, $pages: InputPagesInput!) {
    notesCollectionsList(parentId: null, archived: $archived, pages: $pages) {
        total
        page
        maxPage
        items {
            ...CollectionProps
        }
    }
}`;

export function useCollectionsTreeQuery(page: number) {
    return useQuery(COLLECTIONS_TREE, {
        variables: {
            archived: "ALL",
            pages: {
                page: page,
            },
        },
    });
}

const COLLECTIONS_NEW = gql`
${COLLECTION_PROPS}
mutation CollectionsNew($name: String!, $view: InputEnumCollectionView) {
    notesCollectionsCreate(name: $name, view: $view) {
        ...CollectionProps
    }
}`;

export function useCollectionsNewMutation() {
    return useMutation(COLLECTIONS_NEW, {
        refetchQueries: [
            COLLECTIONS_TREE,
        ],
    });
}

const COLLECTIONS_GET = gql`
${COLLECTION_PROPS}
query CollectionsGet($slug: String!) {
    notesCollectionsGet(idOrSlug: $slug) {
        ...CollectionProps
    }
}`;

export function useCollectionsGetQuery(slug: string) {
    return useQuery(COLLECTIONS_GET, {
        variables: {
            slug: slug,
        },
    });
}
