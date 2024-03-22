function isListItem(md: string, idx: number, maxIdx: number) {
    while (idx < maxIdx && md[idx] === " ") {
        idx++;
    }
    return idx < maxIdx - 2 && md.startsWith("- ", idx);
}

function mdToHtmlInternal(md: string, fromIdx: number, toIdx: number, linkify: boolean): string {
    if (fromIdx >= toIdx) { return ""; }
    var htmlParts = [];
    var mdIdx = fromIdx;
    while (mdIdx < toIdx) {
        const paragraphEndIdx = md.indexOf("\n\n", mdIdx);
        if (paragraphEndIdx !== -1 && paragraphEndIdx < toIdx) {
            htmlParts.push(`<div>${mdToHtmlInternal(md, mdIdx, paragraphEndIdx, linkify)}</div>\n`);
            mdIdx = paragraphEndIdx + 2;
        } else if (isListItem(md, mdIdx, toIdx)) {
            var level = -1;
            while (mdIdx < toIdx) {
                if (isListItem(md, mdIdx, toIdx)) {
                    const dashIdx = md.indexOf("-", mdIdx);
                    const lineLevel = Math.floor((dashIdx - mdIdx) / 2);
                    while (level != lineLevel) {
                        if (level < lineLevel) {
                            level++;
                            htmlParts.push("\t".repeat(level));
                            htmlParts.push("<ul>\n");
                        } else {
                            htmlParts.push("\t".repeat(level));
                            htmlParts.push("</ul>\n");
                            level--;
                        }
                    }
                    htmlParts.push("\t".repeat(level + 1));
                    const lineEndIdx = Math.min(md.indexOf("\n", mdIdx), toIdx);
                    htmlParts.push(`<li>${mdToHtmlInternal(md, dashIdx + 1, lineEndIdx, linkify)}</li>\n`);
                    mdIdx = lineEndIdx + 1;
                } else {
                    break;
                }
            }
            while (level >= 0) {
                htmlParts.push("\t".repeat(level));
                htmlParts.push("</ul>\n");
                level--;
            }
        } else {
            var bold = false;
            var italic = false;
            var lineEndIdx = md.indexOf("\n", mdIdx);
            if (lineEndIdx === -1) { lineEndIdx = toIdx; }
            lineEndIdx = Math.min(lineEndIdx, toIdx);
            while (mdIdx < lineEndIdx) {
                if (md.startsWith("**", mdIdx)) { // bold
                    if (bold) { htmlParts.push("</strong>"); bold = false; }
                    else      { htmlParts.push("<strong>");  bold = true;  }
                    mdIdx += 2;
                } else if (md.startsWith("*", mdIdx)) { // italic
                    if (italic) { htmlParts.push("</em>"); italic = false; }
                    else        { htmlParts.push("<em>");  italic = true;  }
                    mdIdx += 1;
                } else if (md.startsWith("[ ] ", mdIdx) || md.startsWith("[x] ", mdIdx)) { // checkbox
                    const checked = md[mdIdx + 1] === "x";
                    htmlParts.push(`<input type="checkbox"${checked ? " checked" : " "}>`);
                    mdIdx += 4;
                } else {
                    htmlParts.push(md[mdIdx]);
                    mdIdx += 1;
                }
            }
            mdIdx = lineEndIdx + 1;
            if (mdIdx < toIdx) { 
                htmlParts.push("\n");
            }
        }
    }
    return htmlParts.join("");
}

export function mdToHtml(md: string, linkify: boolean) {
    md = md.replaceAll("\r\n", "\n");
    return mdToHtmlInternal(md, 0, md.length, linkify);
}

export function htmlToMd(root: HTMLElement) {
    var md = "";
    if (root.nodeType === Node.ELEMENT_NODE) {
        const children = Array.from(root.childNodes);
        if (root.tagName.toLowerCase() === "div") {
            for (const child of children) {
                md += htmlToMd(child);
            }
            md += "\n\n";
        } else if (root.tagName.toLowerCase() === "ul") {
            for (const listItem of children) {
                if (listItem.nodeType === Node.ELEMENT_NODE && listItem.tagName.toLowerCase() === "li") {
                    md += ` - ${htmlToMd(listItem)}\n`;
                } else {
                    // something else in the list, besides a <li>
                }
            }
        } else if (root.tagName.toLowerCase() === "a") {
            const href = root.getAttribute("href");
            var text = "";
            for (const child of children) {
                text += htmlToMd(child);
            }
            md += `[${text}](${href})`;
        } else if (root.tagName.toLowerCase() === "br") {
            md += "\n";
        } else if (root.tagName.toLowerCase() === "input") {
            const checked = root.getAttribute("checked") === "checked";
            md += `[${checked ? "x" : " "}] `;
        } else {
            // something else in the root
            for (const listItem of children) {
                md += htmlToMd(listItem);
            }
        }
    } else if (root.nodeType === Node.TEXT_NODE) {
        return root.textContent?.replace("\n", " ") || "";
    }
    return md.split("\n").map((line) => line.trim()).join("\n");
}
