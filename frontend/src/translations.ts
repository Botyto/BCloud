import profileTranslations from "./views/profile/translations";
import filesTransations from './views/files/translations';
import notesTranslations from './views/notes/translations';

export const en = {
    common: {
        homepage: {
            "hi": "Hi",
            "hi_user": "Hi {{user}}",
        },
        "404_not_found": "404 Not Found",
        profile: profileTranslations,
        files: filesTransations,
        notes: notesTranslations,
        loading: "Loading...",
    },
};
