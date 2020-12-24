import os
import requests
import re

from threading import Thread, Lock
from queue import Queue, Empty
from urllib.parse import urlparse
from typing import Set, Dict
from yarl import URL

from crawler.parser import Parser

lock = Lock()


class Page:
    def __init__(self, url: URL, parent=None, origin_directory='log'):
        self.url = url
        self.parent = parent
        self.origin_directory = origin_directory
        self.children_directory = os.path.join(
                origin_directory,
                re.sub(r'[\\/?:*"><]', '_', self.link) + '_children')

    def __hash__(self):
        return hash(str(self.link))

    def __eq__(self, other):
        return self.link == other.link

    def __str__(self):
        return self.link

    @property
    def link(self):
        return str(self.url)

    def update_directory(self):
        if self.parent:
            self.children_directory = os.path.join(
                self.parent.children_directory,
                re.sub(r'[\\/?:*"><]', '_', self.link) + '_children')


class Crawler:
    urls: Queue
    request: Set[str]
    seen_urls: Set[str]
    max_count_urls: int
    visited_urls_count: int
    white_domains: list
    result_urls: Set[Page]
    current_threads: Dict[str, Thread]
    directory_for_download: str
    seen_hosts: Set[str]
    disallow_urls: Set
    download: bool

    def __init__(self, start_url, request, white_domains, max_urls_count=10,
                 directory_for_download='log', download=False):
        self.urls = Queue()
        self.urls.put(Page(URL(start_url), origin_directory=directory_for_download))
        self.result_urls: Set[Page] = set()
        self.max_count_urls = max_urls_count
        self.visited_urls_count = 0
        self.request = set(word.strip().lower() for word in request)
        self.seen_urls = set()
        self.white_domains = white_domains
        self.current_threads = {}
        self.directory_for_download = directory_for_download
        self.seen_hosts = set()
        self.disallow_urls = set()
        self.download = download

    def fill_disallow_urls(self, url: str):
        parser = Parser(url)
        host = parser.host
        if host in self.seen_hosts:
            return
        self.seen_hosts.add(host)
        robots_txt_url = parser.host + 'robots.txt'
        robots_txt = requests.get(robots_txt_url).text.lower()
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
                    lock.acquire()
                    self.disallow_urls.add(
                        re.compile(fr"{host}{string[1][2::]}", re.IGNORECASE))
                    lock.release()
        except IndexError:
            pass

    def analyze_robot(self, url: str) -> bool:
        lock.acquire()
        for reg_dis_url in self.disallow_urls:
            if re.search(reg_dis_url, url):
                lock.release()
                return True
        lock.release()
        return False

    def get_html(self, url: str):
        try:
            self.fill_disallow_urls(url)
            return requests.get(url).text
        except (requests.exceptions.MissingSchema,
                requests.exceptions.ConnectionError,
                requests.exceptions.InvalidSchema,
                requests.exceptions.ContentDecodingError):
            return None

    def write_html(self, page: Page, html: str):
        reg_exp = re.compile(r'[\\/?:*"><]')
        name = re.sub(reg_exp, '_', page.link)
        os.makedirs(self.directory_for_download, exist_ok=True)
        if page.parent is not None:
            page_path = page.parent.children_directory
            os.makedirs(page_path, exist_ok=True)
            with open(f'{page_path}/{name}.html', 'w',
                      encoding='utf-8') as writing:
                writing.write(html)
        else:
            with open(f'{self.directory_for_download}/{name}.html',
                      'w', encoding='utf-8') as writing:
                writing.write(html)

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
        lock.acquire()
        for page in self.result_urls:
            current_page = page
            page_parent = Page(current_page.url.parent)
            # Поиск ближайшего родственника
            while current_page != page_parent:
                if page_parent in self.result_urls:
                    page.parent = page_parent
                    page.update_directory()
                    break
                current_page = page_parent
                page_parent = Page(page_parent.url.parent)
            # Поиск непосредственного родителя
            # if page_parent in self.result_urls:
            #     page.parent = page_parent

        lock.release()

    def analyze_url(self, page: Page):
        try:
            self.visited_urls_count += 1
            self.seen_urls.add(page.link)
            if not self.check_domains(page.link):
                self.current_threads.pop(page.link)
                return
            html = self.get_html(page.link)
            if html is None:
                self.current_threads.pop(page.link)
                return
            if self.analyze_robot(page.link):
                self.current_threads.pop(page.link)
                return
            if self.visited_urls_count <= self.max_count_urls:
                parser = Parser(page.link)
                info = parser.get_info(html, page.link)
                if len(self.request.intersection(info)) != 0 \
                        and page not in self.result_urls:
                    self.result_urls.add(page)
                    self.update_parents()
                    if self.download:
                        self.write_html(page, html)
                found_links = set(parser.get_urls(html))
                for link in found_links.difference(self.seen_urls):
                    if link[-1] == '/':
                        page = Page(URL(link[:-1]))
                    else:
                        page = Page(URL(link))
                    self.urls.put(page)
            else:
                return
        finally:
            self.current_threads.pop(page.link, None)

    def crawl(self):
        while self.visited_urls_count < self.max_count_urls:
            if not self.current_threads and self.urls.empty():
                break
            if len(self.current_threads) < self.max_count_urls:
                try:
                    page = self.urls.get(timeout=3)
                    if page.link in self.seen_urls:
                        continue
                except Empty:
                    if not self.current_threads:
                        break
                thread = Thread(target=self.analyze_url, args=(page,))
                self.current_threads[page.link] = thread
                thread.start()
        lock.acquire()
        undone_threads = list(self.current_threads.values())
        lock.release()
        for thread in undone_threads:
            if thread.is_alive():
                thread.join()
        return self.result_urls
