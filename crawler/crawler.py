import requests
from threading import Thread
import re
from urllib.parse import urlparse
from crawler.parser import Parser


class Crawler(object):
    urls: []
    request: [str]
    seen_urls: {str}
    max_count_urls: int
    visited_urls_count: int
    white_domains: []
    result_urls: {str}

    def __init__(self, start_url, request, white_domains, max_urls_count=10):
        self.urls = []
        self.result_urls = set()
        self.urls.append(start_url)
        self.max_count_urls = max_urls_count
        self.visited_urls_count = 0
        self.request = request
        self.seen_urls = set()
        self.white_domains = white_domains

    @staticmethod
    def get_html(url):
        try:
            return requests.get(url).text
        except requests.exceptions:
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

    def analysis_url(self, url):
        self.visited_urls_count += 1
        if not self.check_domains(url):
            return
        html = Crawler.get_html(url)
        if html is None:
            return
        parser = Parser(url)
        found_links = parser.get_urls(html)
        info = parser.get_info(html, url)
        for link in found_links:
            if link not in self.urls and link not in self.seen_urls:
                self.urls.append(link)
                self.seen_urls.add(link)
        for word in self.request:
            for control_word in info:
                if word.lower() in control_word.lower() and url not in self.result_urls:
                    print(url)
                    self.result_urls.add(url)
                    Crawler.write_html(url, html)

    def searcher(self):
        while self.visited_urls_count < self.max_count_urls and len(self.urls) != 0:
            for url in self.urls:
                thread = Thread(self.analysis_url(url))
                thread.start()
                self.urls.remove(url)
                if self.visited_urls_count > self.max_count_urls:
                    return self.result_urls
        return self.result_urls
