import React from 'react';
import { Route } from "react-router-dom";

import Browser from './Browser';
import Storages from './Storages';

export default [
    <Route path="/files" element={<Storages/>} />,
    <Route path="/files/:storageId/*" element={<Browser/>} />,
];
