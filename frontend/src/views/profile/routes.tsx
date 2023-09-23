import React from 'react';
import { Route } from "react-router-dom";

import Login from "./Login";
import Activity from "./Activity";

export default [
    <Route path="/profile/login" element={<Login/>} />,
    <Route path="/profile/activity" element={<Activity/>} />
];
