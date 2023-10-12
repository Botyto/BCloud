import React from 'react';
import { Route } from "react-router-dom";

import Login from "./Login";
import Activity from "./Activity";
import Importing from "./Importing";

export default [
    <Route path="/profile/login" element={<Login/>} />,
    <Route path="/profile/activity" element={<Activity />} />,
    <Route path="/profile/import" element={<Importing/>} />,
];
