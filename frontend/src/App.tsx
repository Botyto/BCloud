import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import Layout from "./views/Layout";
import Homepage from "./views/Homepage";
import NotFound from "./views/NotFound";

import ProfileRoutes from "./views/profile/routes";

export default function App() {
    return <BrowserRouter>
        <Routes>
            <Route path="/" element={<Layout/>}>
                <Route index element={<Homepage/>}/>
                {...ProfileRoutes}
                <Route path="*" element={<NotFound/>} />
            </Route>
        </Routes>
    </BrowserRouter>;
}
