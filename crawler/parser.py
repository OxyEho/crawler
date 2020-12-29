import re
from typing import List, Set
from bs4 import BeautifulSoup
from yarl import URL


class Parser:
    host: URL
    description_finder = re.compile(r'<meta [\w:]+="[\w:" ]+="([^>]+)"/>')
    title_finder = re.compile(r'<title>(.+)</title>')

    def __init__(self, url: URL):
        self.host = url.origin()

    def get_urls(self, page: str) -> List[URL]:
        soup = BeautifulSoup(page, 'html.parser')
        result = []
        for link in soup.find_all('a', href=True):
            if link['href'].startswith('/'):
                result.append(self.host / link['href'][1:])
            elif '#' not in link['href']:
                result.append(URL(link['href']))
        return result

    @staticmethod
    def get_info(html: str, url: str) -> Set[str]:
        info = []
        url_info = re.split(r'[\-:./\d]+', url)
        info += url_info
        if html is not None:
            description = re.findall(Parser.description_finder, html)
            title = re.search(Parser.title_finder, html)
            if description is not None:
                info = info + description
            if title is not None:
                info = info + title.group(1).split()
        set_info = set(word.strip().lower() for word in info)
        set_info.add('')
        return set_info
