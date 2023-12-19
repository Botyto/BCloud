import { FieldFunctionOptions, TypePolicies, gql, useMutation, useQuery } from '@apollo/client';

export const NOTES_FIELD_POLICY: TypePolicies = {
    Query: {
        fields: {
            notesNotesList: {
                keyArgs: false,
                merge(existing: any, incoming: any, options: FieldFunctionOptions) {
                    if (!existing) {
                        return incoming;
                    } else {
                        return {
                            ...incoming,
                            items: [...existing.items, ...incoming.items],
                        };
                    }
                }
            },
        },
    },
};

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
        page
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

const ATTACH_FILE = gql`
${NOTE_PROPS}
mutation AttachNoteFile($noteId: UUID!, $kind: InputFileKind!, $mimeType: String!) {
    notesNoteAttachmentsAddAttachment(noteId: $noteId, kind: $kind, mimeType: $mimeType) {
        note {
            ...NoteProps
        }
        file {
            id
        }
    }
}`;
