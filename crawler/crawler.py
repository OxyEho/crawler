import requests
import re

from multiprocessing.pool import ThreadPool
from queue import Queue, Empty
from urllib.parse import urlparse
from typing import Set
from yarl import URL
from pathlib import Path

from crawler.parser import Parser


class Page:
    def __init__(self, url: URL):
        self.url = url
        self.parent = None

    def __hash__(self):
        return hash(str(self._link))

    def __eq__(self, other):
        if isinstance(other, Page):
            return self.url == other.url
        return False

    def __str__(self):
        return self._link

    @property
    def _link(self):
        return str(self.url)


class Crawler:
    urls: Queue
    request: Set[str]
    seen_urls: Set[Page]
    max_count_urls: int
    visited_urls_count: int
    white_domains: list
    result_urls: Set[Page]
    origin_directory: str
    seen_hosts: Set[URL]
    disallow_urls: Set
    download: bool

    def __init__(self, start_url, request, white_domains, max_urls_count=10,
                 directory_for_download='pages', download=False):
        self.urls = Queue()
        self.urls.put(Page(URL(start_url)))
        self.result_urls: Set[Page] = set()
        self.max_count_urls = max_urls_count
        self.visited_urls_count = 0
        self.request = set(word.strip().lower() for word in request)
        self.seen_urls = set()
        self.white_domains = white_domains
        self.origin_directory = directory_for_download
        self.seen_hosts = set()
        self.disallow_urls = set()
        self.download = download
        self.thread_pool = ThreadPool(processes=10)

    def fill_disallow_urls(self, url: URL):
        parser = Parser(url)
        host = parser.host
        if host in self.seen_hosts:
            return
        self.seen_hosts.add(host)
        robots_txt_url = parser.host / 'robots.txt'
        robots_txt = requests.get(str(robots_txt_url)).text.lower()
        try:
            index = robots_txt.index('user-agent: *')
        except ValueError:
            return
        robots_txt = robots_txt[index::]
        robots_txt = robots_txt.split('\n')
        try:
            for string in robots_txt:
                if string.startswith('disallow'):
                    string = string.replace('*', '.+')
                    string = string.split(':')
                    self.disallow_urls.add(
                        re.compile(fr"{host}/{string[1][2::]}",
                                   re.IGNORECASE))
        except IndexError:
            pass

    def analyze_robot(self, url: URL) -> bool:
        for reg_dis_url in self.disallow_urls:
            if re.search(reg_dis_url, str(url)):
                return True
        return False

    def get_html(self, url: URL):
        try:
            self.fill_disallow_urls(url)
            return requests.get(str(url)).text
        except (requests.exceptions.MissingSchema,
                requests.exceptions.ConnectionError,
                requests.exceptions.InvalidSchema,
                requests.exceptions.ContentDecodingError):
            return None

    def write_html(self, page: Page, html: str):
        host = page.url.host
        origin_directory = self.origin_directory
        parent_path = Path(origin_directory) / host / page.url.parent.path[1:]
        parent_path.mkdir(parents=True, exist_ok=True)
        # Добавляю _page поскольку имя файла и директории не могут совпадать
        name = page.url.name
        if name == '':
            name = page.url.host
        path = parent_path / f'{name}_page'
        with path.open('w', encoding='utf-8') as file:
            file.write(html)

    def check_domains(self, url: str):
        if len(self.white_domains) == 0:
            return True
        current_domain = urlparse(url).netloc
        for domain in self.white_domains:
            if type(domain) is str:
                if domain == current_domain:
                    return True
            else:
                if re.search(domain, current_domain):
                    return True
        return False

    def update_parents(self):
        for page in self.result_urls:
            current_page = page
            page_parent = Page(current_page.url.parent)
            while current_page != page_parent:
                if page_parent in self.result_urls:
                    page.parent = page_parent
                    break
                current_page = page_parent
                page_parent = Page(page_parent.url.parent)

    def analyze_url(self, page: Page):
        self.seen_urls.add(page)
        if not self.check_domains(str(page)):
            return
        html = self.get_html(page.url)
        if html is None:
            return
        if self.analyze_robot(page.url):
            return
        if self.visited_urls_count < self.max_count_urls:
            self.visited_urls_count += 1
            parser = Parser(page.url)
            info = parser.get_info(html, str(page))
            if len(self.request.intersection(info)) != 0 \
                    and page not in self.result_urls:
                self.result_urls.add(page)
                self.update_parents()
                if self.download:
                    self.write_html(page, html)
            found_links = set(parser.get_urls(html))
            for link in found_links.difference(self.seen_urls):
                if link:
                    if str(link)[-1] == '/':
                        page = Page(link.parent)
                    else:
                        page = Page(link)
                    self.urls.put(page)
        else:
            return

    def crawl(self):
        while self.visited_urls_count < self.max_count_urls:
            try:
                page = self.urls.get(timeout=1)
                if page in self.seen_urls:
                    continue
            except Empty:
                break
            self.thread_pool.apply_async(self.analyze_url, args=(page,))
        return self.result_urls

    def close(self):
        self.thread_pool.terminate()
        self.thread_pool.join()
