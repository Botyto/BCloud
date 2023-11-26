import { gql, useMutation, useQuery } from '@apollo/client';

const NOTE_PROPS = gql`
fragment NoteProps on NotesNote {
    id
    createdAtUtc
    sortKey
    title
    content
}
`;

const NOTES_LIST = gql`
${NOTE_PROPS}
query NotesList($collectionId: Int!, $archived: InputEnumArchivedFilter!, $pages: InputPagesInput!) {
    notesNotesList(collectionId: $collectionId, archived: $archived, pages: $pages) {
        total
        maxPage
        items {
            ...NoteProps
        }
    }
}`;

export function useNotesListQuery(collectionId: number, page: number) {
    return useQuery(NOTES_LIST, {
        variables: {
            collectionId: collectionId,
            archived: "ALL",
            pages: {
                page: page,
                sort: ["-created_at_utc"]
            }
        }
    });
}

const CREATE_NOTE = gql`
${NOTE_PROPS}
mutation CreateNote($collectionId: Int!, $title: String!, $content: String!, $tags: [String!]!) {
    notesNotesCreate(collectionId: $collectionId, title: $title, content: $content, tags: $tags) {
        ...NoteProps
    }
}`;

export function useCreateNoteMutation() {
    return useMutation(CREATE_NOTE, {
        refetchQueries: [NOTES_LIST],
    });
}
