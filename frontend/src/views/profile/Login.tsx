import React, { useState, MouseEvent } from 'react';
import { gql, useMutation } from '@apollo/client';
import { useNavigate } from 'react-router';

const LOGIN = gql`
mutation Login($username: String!, $password: String!) {
    profileAuthLogin(username: $username, password: $password) {
        jwt
    }
}`;

const REGISTER = gql`
mutation Register($username: String!, $password: String!) {
    profileAuthRegister(username: $username, password: $password) {
        jwt
    }
}`;

export default function Login() {
    const [username, setUsername] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [error, setError] = useState<string>('');
    const [login, loginVars] = useMutation(LOGIN);
    const [register, registerVars] = useMutation(REGISTER);
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
            Login<br/>
            Username: <input type="text" value={username} onChange={(v) => setUsername(v.target.value)}/><br/>
            Password: <input type="password" value={password} onChange={(v) => setPassword(v.target.value)}/><br/>
            <button onClick={onLogin}>Login</button>
            <button onClick={onRegister}>Register</button>
        </form>
        <span style={{color: "red"}}>{error}</span>
    </>;
}
