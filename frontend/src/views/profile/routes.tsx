import React from 'react';
import { Route } from "react-router-dom";

import Login from "./Login";
import Activity from "./Activity";
import Manager from "./importing/Manager";
import Google from './importing/Google';

export default [
    <Route path="/profile/login" element={<Login/>} />,
    <Route path="/profile/activity" element={<Activity />} />,
    <Route path="/profile/import" element={<Manager />} />,
    <Route path="/profile/import/google" element={<Google/>} />,
];
