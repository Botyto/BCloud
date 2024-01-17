export function mdToHtml(md: string) {
    return md.replaceAll("\n", "<br/>");
}

export function htmlToMd(html: string) {
    return html.replaceAll("<br/>", "\n");
}