export default {
    storages: {
        back_to_homepage: "homepage",
        title: "Storages",
        browse: "Browse",
        rename: {
            prompt: "New name for `{{name}}`",
            button: "Rename",
        },
        delete: {
            prompt: "Confirm deletion of `{{name}}`",
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
            upload: {
                button: "Upload",
            },
            all: {
                move: {
                    prompt_one: "Move {{count}} file",
                    prompt_other: "Move {{count}} files",
                    button: "➡️ Move",
                },
                copy: {
                    prompt_one: "Copy {{count}} file",
                    prompt_other: "Copy {{count}} files",
                    button: "📋 Copy",
                },
                delete: {
                    prompt_one: "Confirm deletion of {{count}} file",
                    prompt_other: "Confirm deletion of {{count}} files",
                    button: "❌ Delete"
                },
            },
            file: {
                rename: {
                    prompt: "New name for `{{name}}`",
                    button: "📝 Rename",
                },
                move: {
                    prompt: "Move `{{name}}`",
                    action: "Move here",
                    button: "➡️ Move",
                },
                copy: {
                    prompt: "Copy `{{name}}`",
                    action: "Copy here",
                    button: "📋 Copy",
                },
                delete: {
                    prompt: "Confirm deletion of `{{name}}`",
                    button: "❌ Delete",
                },
                share: {
                    button: "📢 Share",
                },
                link: {
                    prompt: "Link `{{name}}`",
                    action: "Save link",
                    input_label: "Link name",
                    button: "🔗 Add link",
                },
            },
        },
        file: {
            no_content: "No file contents...",
            download: "Download",
            preview: {
                unknown_file_type: "Unknown file type",
                video_not_supported: "Your browser doesn't support the video playback!",
                audio_not_supported: "Your browser doesn't support the audio playback!",
            },
        },
        link: {
            follow: "Follow link...",
        },
        unknown_file_type: "Unknown file type {{type}}",
    },
};