import React, { useEffect, useRef } from 'react';

class DialogState {
    opened: boolean;
    setOpened: (opened: boolean) => void;
    closeOnOutside: boolean;

    constructor(
        opened: boolean,
        setOpened: (opened: boolean) => void,
        closeOnOutside: boolean = true,
    ) {
        this.opened = opened;
        this.setOpened = setOpened;
        this.closeOnOutside = closeOnOutside;
    }

    open() {
        if (this.opened) { return; }
        this.setOpened(true);
    }

    close() {
        if (!this.opened) { return; }
        this.setOpened(false);
    }

    toggle() {
        this.setOpened(!this.opened);
    }
}

export function useDialogState(
    closeOnOutside: boolean = true,
) {
    const [opened, setOpened] = React.useState(false);
    return new DialogState(opened, setOpened, closeOnOutside);
}

interface PublicDialogProps {
    opened: boolean;
    closeOnOutside: boolean;
    alwaysRenderChildren?: boolean;
    onOpen?: () => void;
    onClose?: () => void;
    children: React.ReactNode;
}

interface DialogProps extends PublicDialogProps {
    close: () => void;
}

export function bindState(state: DialogState) {
    return {
        opened: state.opened,
        closeOnOutside: state.closeOnOutside,
        close: state.close.bind(state),
    }
}

function isClickInsideRectangle(e: React.MouseEvent, element: HTMLElement) {
    const r = element.getBoundingClientRect();
    return e.clientX > r.left && e.clientX < r.right && e.clientY > r.top && e.clientY < r.bottom;
};

export function Dialog(props: DialogProps|any) {
    const ref = useRef<HTMLDialogElement>(null);

    useEffect(() => {
        if (props.opened) {
            props.onOpen?.();
            ref.current?.showModal();
        } else {
            props.onClose?.();
            ref.current?.close();
        }
    }, [props]);

    function handleClick(e: React.MouseEvent) {
        if (!props.closeOnOutside) { return; }
        if (!ref.current) { return; }
        if (isClickInsideRectangle(e, ref.current)) { return; }
        props.onClose?.();
        props.close();
    }

    const style: React.CSSProperties = {
        padding: 0,
        border: "none",
        background: "none",
    };
    if ("style" in props) {
        Object.assign(style, props.style);
    }
    const otherProps = Object.assign({}, props);
    delete otherProps.opened;
    delete otherProps.closeOnOutside;
    delete otherProps.close;
    delete otherProps.onClose;
    delete otherProps.onOpen;
    delete otherProps.children;
    delete otherProps.style;

    return <dialog
        ref={ref}
        onClick={handleClick}
        onCancel={() => {props.onClose?.(); props.close();}}
        style={style}
        {...otherProps}
    >
        {props.opened && props.children}
    </dialog>
}
