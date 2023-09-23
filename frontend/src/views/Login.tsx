import React, { useState, MouseEvent } from 'react';
import { gql, useMutation } from '@apollo/client';
import { useNavigate } from 'react-router';

const LOGIN_MUTATION = gql`
mutation Login($username: String!, $password: String!) {
    profileAuthLogin(username: $username, password: $password) {
        jwt
    }
}`;

export default function Login() {
    const [username, setUsername] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [login, { loading, error, data}] = useMutation(LOGIN_MUTATION);
    const navigate = useNavigate();

    function onLogin(e: MouseEvent<HTMLButtonElement>) {
        e.preventDefault();
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
                const token = data.identityLogin.token;
                console.log(token);
                navigate("/");
            },
            onError(error) {
                console.log("failed");
                console.error(error);
            },
        })
    }

    function onSignup(e: MouseEvent<HTMLButtonElement>) {
        e.preventDefault();
        console.log("Signup...");
    }

    return <form>
        Login<br/>
        Username: <input type="text" value={username} onChange={(v) => setUsername(v.target.value)}/><br/>
        Password: <input type="password" value={password} onChange={(v) => setPassword(v.target.value)}/><br/>
        <button onClick={onLogin}>Login</button>
        <button onClick={onSignup}>Signup</button>
    </form>;
}
