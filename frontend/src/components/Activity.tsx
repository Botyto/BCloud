import React from 'react';

export interface ActivityProps {
    id: string;
    createdAt: Date;
    issuer: string;
    type: string;
    payload: any;
}

export function ParseRawActivity(raw: any): ActivityProps {
    const createdAt = new Date();
    createdAt.setTime(Date.parse(raw.createdAtUtc));
    return {
        id: raw.id,
        createdAt: createdAt,
        issuer: raw.issuer,
        type: raw.type,
        payload: raw.payload ? JSON.parse(raw.payload) : null,
    };
}

export function FallbackActivity(props: ActivityProps) {
    return <li>
        <div>{props.createdAt.toLocaleString()} {props.issuer} -&gt; {props.type}</div>
        <div>{JSON.stringify(props.payload)}</div>
    </li>;
}

export function GetRenderer(raw: any, renderers: any): React.FC<ActivityProps> {
    return renderers[`${raw.issuer}.${raw.type}`] || FallbackActivity;
}
