import { gql, useQuery } from '@apollo/client';

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
            }
        }
    });
}
