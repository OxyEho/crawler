import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup


class Parser(object):
    host: str
    description_finder = re.compile(r'<meta [\w:]+="[\w:" ]+="([^>]+)"/>')
    title_finder = re.compile(r'<title>(.+)</title>')

    def __init__(self, url: str):
        self.host = Parser.get_host(url)

    def get_urls(self, page: str):
        soup = BeautifulSoup(page, 'html.parser')
        result = []
        for link in soup.find_all('a', href=True):
            if link['href'].startswith('/'):
                result.append(self.host + link['href'])
            elif '#' not in link['href']:
                result.append(link['href'])
        return result

    @staticmethod
    def get_host(url: str):
        parsed_url = urlparse(url)
        return f'{parsed_url.scheme}://{parsed_url.netloc}/'

    @staticmethod
    def get_info(html: str, url: str):
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
        return set(word.strip().lower() for word in info)