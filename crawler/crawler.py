from queue import Queue, Empty
from typing import Set, List
import requests
from threading import Thread
import re
from urllib.parse import urlparse
from crawler.parser import Parser


class Crawler(object):
    urls: Queue
    request: Set[str]
    seen_urls: Set[str]
    max_count_urls: int
    visited_urls_count: int
    white_domains: list
    result_urls: Set[str]

    def __init__(self, start_url, request, white_domains, max_urls_count=10):
        self.urls = Queue()
        self.urls.put(start_url)
        self.result_urls = set()
        self.max_count_urls = max_urls_count
        self.visited_urls_count = 0
        self.request = set(word.strip().lower() for word in request)
        self.seen_urls = set()
        self.white_domains = white_domains
        self.current_threads = {}

    @staticmethod
    def get_html(url):
        try:
            return requests.get(url).text
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            return None

    @staticmethod
    def write_html(url: str, html: str):
        reg_exp = re.compile(r'[\\/?:*"><]')
        name = re.sub(reg_exp, '_', url)
        with open(f'{name}.html', 'w', encoding='utf-8') as writing:
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
        if not self.check_domains(url):
            return
        html = Crawler.get_html(url)
        if html is None:
            return
        self.visited_urls_count += 1
        parser = Parser(url)

        info = parser.get_info(html, url)
        if self.request.intersection(info) and url not in self.result_urls:
            self.result_urls.add(url)
            Crawler.write_html(url, html)

        found_links = set(parser.get_urls(html))
        for link in found_links.difference():
            self.urls.put(link)
        self.current_threads.pop(url)

    def crawl(self):
        while self.visited_urls_count < self.max_count_urls:
            try:
                url = self.urls.get(timeout=10)
                if url in self.seen_urls:
                    continue
            except Empty:
                if not self.current_threads:
                    break

            thread = Thread(target=self.analyze_url, args=(url,))
            self.current_threads[url] = thread
            thread.start()
            if self.visited_urls_count >= self.max_count_urls:
                return self.result_urls
        return self.result_urls
