from dataclasses import dataclass

import requests


@dataclass
class HtmlCache:
    mime_type: str
    content: bytes


class HtmlChacher:
    def cache(self, url: str) -> HtmlCache|None:
        response = requests.get(url)
        if response.text:
            mime_type = response.headers.get("Content-Type", "text/html")
            content = response.content
            return HtmlCache(mime_type, content)
