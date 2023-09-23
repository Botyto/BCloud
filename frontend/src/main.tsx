import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx';
import { ApiManagement } from './ApiManagement.jsx';
import ThemeManagement from './ThemeManagement.jsx';

const root = document.getElementById('root') as HTMLElement;
const reactRoot = ReactDOM.createRoot(root);
reactRoot.render(
    <React.StrictMode>
        <ApiManagement>
            <ThemeManagement>
                <App />
            </ThemeManagement>
        </ApiManagement>
    </React.StrictMode>,
);
