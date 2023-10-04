import React from 'react';
import { Link } from 'react-router-dom';
import { BROWSER_ROUTE } from './browser/common';
import fspath from './fspath';

interface BreadcrumbsPiece {
    name: string;
    url: string;
    current: boolean;
}

export function makeBreadcrumbs(storageName: string, storageId: string, parts: string[]) {
    const result: BreadcrumbsPiece[] = [];
    for (var i = 0; i < parts.length + 1; i++) {
        const subparts = parts.slice(0, i);
        var part = (i === 0) ? storageName : parts[i - 1];
        if (part.startsWith(fspath.sep)) {
            part = part.slice(1);
        }
        result.push({
            name: part,
            url: fspath.pathToUrl(BROWSER_ROUTE, fspath.join(storageId, subparts)),
            current: (i === parts.length),
        });
    }
    return result;
}

interface BreacumbsProps {
    pieces: BreadcrumbsPiece[];
}

export function Breadcrumbs(props: BreacumbsProps) {
    return <span>
        {
            props.pieces.map((piece, i) => {
                return (piece.current) ? (
                    <span key={i}>
                        {piece.name}
                        {(i < props.pieces.length - 1) ? " / " : ""}
                    </span>
                ) : (
                    <span key={i}>
                        <Link to={piece.url}>{piece.name}</Link>
                        {(i < props.pieces.length - 1) ? " / " : ""}
                    </span>
                );
            })
        }
    </span>;
}
