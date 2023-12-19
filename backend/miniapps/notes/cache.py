import requests


class HtmlChacher:
    def cache(self, url: str) -> str:
        return requests.get(url).text
