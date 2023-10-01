import React, { useState, MouseEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useLoginMutation, useRegisterMutation } from './api';


export default function Login() {
    const [username, setUsername] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [error, setError] = useState<string>('');
    const [login, loginVars] = useLoginMutation();
    const [register, registerVars] = useRegisterMutation();
    const navigate = useNavigate();

    function onLogin(e: MouseEvent<HTMLButtonElement>) {
        e.preventDefault();
        setError("");
        login({
            context: {
                headers: {
                    authorization: "",
                },
            },
            variables: {
                username,
                password,
            },
            onCompleted(data, clientOptions) {
                const token = data.profileAuthLogin.jwt;
                localStorage.setItem("authentication-token", token);
                navigate("/");
            },
            onError(error) {
                setError("Login failed: " + error.message);
            },
        });
    }

    function onRegister(e: MouseEvent<HTMLButtonElement>) {
        e.preventDefault();
        setError("");
        register({
            context: {
                headers: {
                    authorization: "",
                },
            },
            variables: {
                username,
                password,
            },
            onCompleted(data, clientOptions) {
                const token = data.profileAuthRegister.jwt;
                localStorage.setItem("authentication-token", token);
                navigate("/");
            },
            onError(error) {
                setError("Registration failed: " + error.message);
            },
        });
    }

    return <>
        <form>
            Login (<Link to="/">homepage</Link>)<br/>
            Username: <input type="text" value={username} onChange={(v) => setUsername(v.target.value)}/><br/>
            Password: <input type="password" value={password} onChange={(v) => setPassword(v.target.value)}/><br/>
            <button onClick={onLogin}>Login</button>
            <button onClick={onRegister}>Register</button>
        </form>
        <span style={{color: "red"}}>{error}</span>
    </>;
}
