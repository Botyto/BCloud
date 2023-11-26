import ViewTranslations from "./views/translations";

export default {
    title: "Notes",
    back_to_homepage: "homepage",
    collections: {
        empty: "No collections yet",
        new: {
            button: "New collection",
            name: "New collection new",
            cancel: "Cancel",
            add: "Add",
            view: {
                notes: "📝 Notes",
                bookmarks: "🔗 Bookmarks",
                chat: "💬 Chat",
            }
        },
    },
    collection: {
        title: "{{name}}",
        error: "Error: {{error}}",
    },
    view: ViewTranslations,
};