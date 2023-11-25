import React from 'react';
import { Route } from "react-router-dom";

import NotesBrowser from "./NotesBrowser";

export default [
    <Route path="/notes" element={<NotesBrowser/>} />,
    <Route path="/notes/:collection" element={<NotesBrowser/>} />,
    <Route path="/notes/:collection/:note" element={<NotesBrowser/>} />,
    <Route path="/notes/:note" element={<NotesBrowser/>} />,
];
