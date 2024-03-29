import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import Layout from "./views/Layout";
import Homepage from "./views/Homepage";
import NotFound from "./views/NotFound";

import ProfileRoutes from "./views/profile/routes";
import FilesRoutes from "./views/files/routes"
import NotesRoutes from "./views/notes/routes"

export default function App() {
    return <BrowserRouter>
        <Routes>
            <Route path="/" element={<Layout/>}>
                <Route index element={<Homepage/>}/>
                {...ProfileRoutes}
                {...FilesRoutes}
                {...NotesRoutes}
                <Route path="*" element={<NotFound/>} />
            </Route>
        </Routes>
    </BrowserRouter>;
}
