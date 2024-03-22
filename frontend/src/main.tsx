import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import { ApiManagement } from './ApiManagement.jsx';
import ThemeManagement from './ThemeManagement.jsx';
import i18next from "i18next";
import { I18nextProvider } from "react-i18next";
import { en } from './translations';

i18next.init({
    lng: "en",
    resources: { en },
})

const root = document.getElementById('root') as HTMLElement;
const reactRoot = ReactDOM.createRoot(root);
reactRoot.render(
    <React.StrictMode>
        <ApiManagement>
            <I18nextProvider i18n={i18next}>
                <ThemeManagement>
                    <App />
                </ThemeManagement>
            </I18nextProvider>
        </ApiManagement>
    </React.StrictMode>,
);
