import requests
from threading import Thread, Lock
import os
import re
from queue import Queue, Empty
from urllib.parse import urlparse
from crawler.parser import Parser
from typing import Set, Dict


lock = Lock()


class Crawler(object):
    urls: Queue
    request: Set[str]
    seen_urls: Set[str]
    max_count_urls: int
    visited_urls_count: int
    white_domains: list
    result_urls: Set[str]
    current_threads: Dict[str, Thread]
    directory_for_download: str
    seen_hosts: Set[str]
    disallow_urls: Set

    def __init__(self, start_url, request, white_domains, max_urls_count=10, directory_for_download='log'):
        self.urls = Queue()
        self.urls.put(start_url)
        self.result_urls = set()
        self.max_count_urls = max_urls_count
        self.visited_urls_count = 0
        self.request = set(word.strip().lower() for word in request)
        self.seen_urls = set()
        self.white_domains = white_domains
        self.current_threads = {}
        self.directory_for_download = directory_for_download
        self.seen_hosts = set()
        self.disallow_urls = set()

    def fill_disallow_urls(self, url):
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
                    print(f'{host}{string[1][2::]}')
                    self.disallow_urls.add(re.compile(fr"{host}{string[1][2::]}", re.IGNORECASE))
        except IndexError:
            pass

    def analyze_robot(self, url):
        lock.acquire()
        for reg_dis_url in self.disallow_urls:
            if re.search(reg_dis_url, url):
                lock.release()
                return True
        lock.release()
        return False

    def get_html(self, url):
        try:
            self.fill_disallow_urls(url)
            return requests.get(url).text
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError,
                requests.exceptions.InvalidSchema, requests.exceptions.ContentDecodingError):
            return None

    def write_html(self, url: str, html: str):
        reg_exp = re.compile(r'[\\/?:*"><]')
        name = re.sub(reg_exp, '_', url)
        os.makedirs(self.directory_for_download, exist_ok=True)
        with open(f'{self.directory_for_download}/{name}.html', 'w', encoding='utf-8') as writing:
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

    def analyze_url(self, url):
        try:
            self.seen_urls.add(url)
            if not self.check_domains(url):
                self.current_threads.pop(url)
                return
            html = self.get_html(url)
            if html is None:
                self.current_threads.pop(url)
                return
            if self.analyze_robot(url):
                self.current_threads.pop(url)
                return
            if self.visited_urls_count <= self.max_count_urls:
                self.visited_urls_count += 1
                parser = Parser(url)
                info = parser.get_info(html, url)
                if len(self.request.intersection(info)) != 0 and url not in self.result_urls:
                    self.result_urls.add(url)
                    self.write_html(url, html)
                found_links = set(parser.get_urls(html))
                for link in found_links.difference(self.seen_urls):
                    self.urls.put(link)
            else:
                return
        finally:
            self.current_threads.pop(url, None)

    def crawl(self):
        while self.visited_urls_count < self.max_count_urls:
            if not self.current_threads and self.urls.empty():
                break
            if len(self.current_threads) < self.max_count_urls:
                try:
                    url = self.urls.get(timeout=3)
                    if url in self.seen_urls:
                        continue
                except Empty:
                    if not self.current_threads:
                        break
                thread = Thread(target=self.analyze_url, args=(url,))
                self.current_threads[url] = thread
                thread.start()
        lock.acquire()
        undone_threads = list(self.current_threads.values())
        lock.release()
        for thread in undone_threads:
            if thread.is_alive():
                thread.join()
        return self.result_urls
