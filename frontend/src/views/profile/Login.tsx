import React, { useState, MouseEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';
import { useLoginMutation, useRegisterMutation } from './api';


export default function Login() {
    const { t } = useTranslation("common");
    const [username, setUsername] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [error, setError] = useState<string>('');
    const [login, loginVars] = useLoginMutation();
    const [register, registerVars] = useRegisterMutation();
    const navigate = useNavigate();

    function setAuthToken(token: string) {
        localStorage.setItem("authentication-token", token);
        document.cookie = "Authorization=Bearer " + token + "; SameSite=None; Secure";
    }

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
            onCompleted(data) {
                const token = data.profileAuthLogin.jwt;
                setAuthToken(token);
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
            onCompleted(data) {
                const token = data.profileAuthRegister.jwt;
                setAuthToken(token);
                navigate("/");
            },
            onError(error) {
                setError("Registration failed: " + error.message);
            },
        });
    }

    return <>
        <form>
            {t("profile.login.title")} (<Link to="/">{t("profile.back_to_homepage")}</Link>)<br/>
            {t("profile.login.username_label")}:
            <input type="text" value={username} onChange={(v) => setUsername(v.target.value)} /><br />
            {t("profile.login.password_label")}:
            <input type="password" value={password} onChange={(v) => setPassword(v.target.value)} /><br />
            <button onClick={onLogin}>{t("profile.login.login_button")}</button>
            <button onClick={onRegister}>{t("profile.login.register_button")}</button>
        </form>
        <span style={{color: "red"}}>{error}</span>
    </>;
}
