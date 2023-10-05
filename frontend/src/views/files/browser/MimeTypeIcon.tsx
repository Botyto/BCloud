interface MimeTypeIconProps {
    type: string;
    mimeType?: string;
}

export default function MimeTypeIcon(props: MimeTypeIconProps) {
    switch (props.type) {
        case "FILE":
            return "📄";
        case "DIRECTORY":
            return "📁";
        case "LINK":
            return "🔗";
        default:
            return "❓";
    }
}