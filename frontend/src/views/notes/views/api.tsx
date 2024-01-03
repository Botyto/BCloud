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
fragment NoteFileProps on NotesFile {
    id
    kind
    file {
        id
        abspath
        mimeType
    }
}
fragment NoteProps on NotesNote {
    id
    createdAtUtc
    sortKey
    title
    content
    files {
        ...NoteFileProps
    }
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
mutation AttachNoteFile($noteId: UUID!, $kind: InputEnumFileKind!, $mimeType: String!) {
    notesNoteattachmentsAddAttachment(noteId: $noteId, kind: $kind, mimeType: $mimeType) {
        note {
            ...NoteProps
        }
        file {
            id
            abspath
        }
    }
}`;

export function useAttachFileMutation() {
    return useMutation(ATTACH_FILE, {
        refetchQueries: [NOTES_LIST],
    });
}

const NOTE_SET_ARCHIVED = gql`
${NOTE_PROPS}
mutation ArchiveNoteMutation($id: UUID!, $archived: Boolean!) {
    notesNotesSetArchived(id: $id, archived: $archived) {
        ...NoteProps
    }
}`;

export function useArchiveNoteMutation() {
    return useMutation(NOTE_SET_ARCHIVED, {
        refetchQueries: [NOTES_LIST],
    });
}

const DELETE_NOTE = gql`
mutation DeleteNoteMutation($id: UUID!) {
    notesNotesDelete(id: $id) {
        success
    }
}`;

export function useDeleteNoteMutation() {
    return useMutation(DELETE_NOTE, {
        refetchQueries: [NOTES_LIST],
    });
}
