import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

const root = document.getElementById('root');
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
