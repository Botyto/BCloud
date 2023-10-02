interface MimeTypeIconProps {
    type: string;
    mimeType?: string;
}

export default function MimeTypeIcon(props: MimeTypeIconProps) {
    switch (props.type) {
        case "FILE":
            return "[F]";
        case "DIRECTORY":
            return "[D]";
        case "LINK":
            return "[L]";
        default:
            return "[?]";
    }
}