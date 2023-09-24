import React from 'react';
import { Route } from "react-router-dom";

import Storages from './Storages';

export default [
    <Route path="/files" element={<Storages/>} />,
];
