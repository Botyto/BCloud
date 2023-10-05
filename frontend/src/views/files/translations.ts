export default {
    storages: {
        back_to_homepage: "homepage",
        title: "Storages",
        browse: "Browse",
        rename: {
            prompt: "New name for {{storage.name}}",
            button: "Rename",
        },
        delete: {
            prompt: "Confirm deletion of {{storage.name}}",
            button: "Delete",
        },
        create: "Create",
    },
    browser: {
        back_to_storages: "storages",
        title: "Browser",
        breadcrumbs: "Path",
        error: "Error: {{error}}",
        dir: {
            empty: "Empty...",
            new_file: {
                prompt: "File name",
                button: "New file",
            },
            new_dir: {
                prompt: "Directory name",
                button: "New directory",
            },
            all: {
                move: "Move",
                copy: "Copy",
                delete: {
                    prompt_one: "Confirm deletion of {{count}} file",
                    prompt_other: "Confirm deletion of {{count}} files",
                    button: "Delete"
                },
            },
            file: {
                rename: {
                    prompt: "New name for {{file.name}}",
                    button: "Rename",
                },
                move: "Move",
                copy: "Copy",
                delete: {
                    prompt: "Confirm deletion of {{file.name}}",
                    button: "Delete",
                },
                share: "Share",
                link: "Add link",
            },
        },
        file: {
            no_content: "No file contents...",
            download: "Download",
            preview: {
                unknown_file_type: "Unknown file type",
            },
        },
        link: {
            follow: "Follow link...",
        },
        unknown_file_type: "Unknown file type {{type}}",
    },
};