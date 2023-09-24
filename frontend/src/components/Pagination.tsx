import React, { MouseEvent } from 'react';

interface PaginationProps {
    radius: number;
    onSetPage: (page: number) => void;
    page: number;
    maxPage: number;
}

export default function Pagination(props: PaginationProps) {
    const radius = props.radius || 3;
    const currentPage = props.page || 0;
    const minPage = Math.max(0, currentPage - radius);
    const maxPage = Math.min(props.maxPage || 0, currentPage + radius);
    const shownPages = [];
    for (let i = minPage; i <= maxPage; i++) {
        shownPages.push(i);
    }
    const hasPrevious = currentPage > 0;
    const hasNext = currentPage < (props.maxPage || 0);

    function changePage(e: MouseEvent<HTMLButtonElement>, page: number) {
        e.preventDefault();
        props.onSetPage(page);
    }

    return <span>
        <button disabled={!hasPrevious}>&lt;</button>
        {
            shownPages.map((page) => {
                return <button
                    disabled={page == currentPage}
                    onClick={e => changePage(e, page)}
                >
                    {page}
                </button>;
            })
        }
        <button disabled={!hasNext}>&gt;</button>
    </span>;
}
