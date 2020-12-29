import unittest
import re
import requests

from unittest.mock import patch
from yarl import URL

from crawler.crawler import Crawler, Page


class FakeResponse:
    text: str


class TestsCrawler(unittest.TestCase):
    def test_crawler_zero_result(self):
        with patch.object(Crawler, 'get_html') as mock_get_html:
            mock_get_html.return_value = '<a href=https://scala1.html></a>'
            with patch.object(Crawler, 'write_html') as mock_write_html:
                mock_write_html.return_value = None
                test_crawler = Crawler(
                    'https://docs.scala-lang.org/ru/tour/tour-of-scala.html',
                    ['dog'],
                    {},
                    2)
                test_result = test_crawler.crawl()
                self.assertEqual(test_result, set())

    def test_searcher_with_result(self):
        with patch.object(Crawler, 'get_html') as mock_get_html:
            mock_get_html.return_value = '<a href=https://scala1.html></a>' \
                                         '<a href=https://scala2.html></a>' \
                                         '<a href=https://scala3.html></a>' \
                                         '<a href=https://scala4.html></a>' \
                                         '<a href=https://scala5.html></a>' \
                                         '<a href=https://scala6.html></a>' \
                                         '<a href=https://scala7.html></a>' \
                                         '<a href=https://scala8.html></a>' \
                                         '<a href=https://scala9.html></a>' \
                                         '<a href=https://scala10.html></a>' \
                                         '<a href=https://scala11.html></a>'
            with patch.object(Crawler, 'write_html') as mock_write_html:
                mock_write_html.return_value = None
                test_crawler = Crawler(
                    'https://docs.scala-lang.org/ru/tour/tour-of-scala.html',
                    ['scala'], {})
                test_result = test_crawler.crawl()
                self.assertEqual(len(test_result), 10)

    def test_searcher_with_seen_urls(self):
        with patch.object(Crawler, 'get_html') as mock_get_html:
            mock_get_html.return_value = '<a href=http://scala-lang.org></a>' \
                                         '<a href=https://scala11.html></a>'
            with patch.object(Crawler, 'write_html') as mock_write_html:
                mock_write_html.return_value = None
                test_crawler = Crawler(
                    'https://docs.scala-lang.org/ru/tour/tour-of-scala.html',
                    ['scala'], {}, 2)
                test_crawler.seen_urls.add('http://scala-lang.org')
                test_result = test_crawler.crawl()
                assert 'http://scala-lang.org' not in test_result

    def test_searcher_with_two_seen_urls(self):
        with patch.object(Crawler, 'get_html') as mock_get_html:
            mock_get_html.return_value = '<a href=http://scala-lang.org></a>' \
                                         '<a href=https://scala11.html></a>' \
                                         '<a href=https://www.scala-lang.org' \
                                         '/download/></a>' \
                                         '<a href=https://scala12.html></a>' \
                                         '<a href=https://scala13.html></a>'
            with patch.object(Crawler, 'write_html') as mock_write_html:
                mock_write_html.return_value = None
                test_crawler = Crawler(
                    'https://docs.scala-lang.org/ru/tour/tour-of-scala.html',
                    ['scala'], {}, 4)
                test_crawler.seen_urls.add('http://scala-lang.org')
                test_crawler.seen_urls.add(
                    'https://www.scala-lang.org/download/')
                test_result = test_crawler.crawl()
                assert 'http://scala-lang.org' not in test_result and \
                       'https://www.scala-lang.org/download/' not in \
                       test_result

    def test_searcher_with_domains(self):
        with patch.object(Crawler, 'get_html') as mock_get_html:
            mock_get_html.return_value = '<a href=https://scala1.html></a>' \
                                         '<a href=https://scala2.html></a>' \
                                         '<a href=https://scala3.html></a>' \
                                         '<a href=https://scala4.html></a>' \
                                         '<a href=https://scala5.html></a>' \
                                         '<a href=https://scala6.html></a>' \
                                         '<a href=https://scala7.html></a>' \
                                         '<a href=https://scala8.html></a>' \
                                         '<a href=https://scala9.html></a>' \
                                         '<a href=https://scala10.html></a>' \
                                         '<a href=https://scala11.html></a>' \
                                         '<a href=https://docs.scala-lang' \
                                         '.org/scala1.html></a> '
            with patch.object(Crawler, 'write_html') as mock_write_html:
                mock_write_html.return_value = None
                test_crawler = Crawler(
                    'https://docs.scala-lang.org/ru/tour/tour-of-scala.html',
                    ['scala'], ['docs.scala-lang.org'])
                test_result = test_crawler.crawl()
                self.assertEqual(len(test_result), 2)

    def test_searcher_with_disallow_url(self):
        with patch.object(Crawler, 'get_html') as mock_get_html:
            mock_get_html.return_value = '<a href=https://scala1.html></a>' \
                                         '<a href=https://scala2.html></a>' \
                                         '<a href=https://scala3.html></a>' \
                                         '<a href=https://scala4.html></a>' \
                                         '<a href=https://scala5.html></a>' \
                                         '<a href=https://scala6.html></a>' \
                                         '<a href=https://scala7.html></a>' \
                                         '<a href=https://scala8.html></a>' \
                                         '<a href=https://scala9.html></a>'
            with patch.object(Crawler, 'write_html') as mock_write_html:
                mock_write_html.return_value = None
                test_crawler = Crawler(
                    'https://docs.scala-lang.org/ru/tour/tour-of-scala.html',
                    ['scala'], {})
                test_crawler.disallow_urls.add(
                    re.compile(r'https://scala5.html'))
                test_result = test_crawler.crawl()
                self.assertEqual(len(test_result), 9)

    def test_searcher_with_disallow_urls(self):
        with patch.object(Crawler, 'get_html') as mock_get_html:
            mock_get_html.return_value = '<a href=https://scala1.html></a>' \
                                         '<a href=https://scala2.html></a>' \
                                         '<a href=https://scala3.html></a>' \
                                         '<a href=https://scala4.html></a>' \
                                         '<a href=https://scala5.html></a>' \
                                         '<a href=https://scala6.html></a>' \
                                         '<a href=https://scala7.html></a>' \
                                         '<a href=https://scala8.html></a>' \
                                         '<a href=https://scala9.html></a>' \
                                         '<a href=https://scala9.html></a>'
            with patch.object(Crawler, 'write_html') as mock_write_html:
                mock_write_html.return_value = None
                test_crawler = Crawler(
                    'https://docs.scala-lang.org/ru/tour/tour-of-scala.html',
                    ['scala'], {})
                test_crawler.disallow_urls.add(
                    re.compile(r'https://scala.*?.html'))
                test_result = test_crawler.crawl()
                self.assertEqual(len(test_result), 1)

    def test_fill_disallow_urls_from_robot(self):
        with patch.object(requests, 'get') as mock_get:
            with open('fake_robots.txt', 'r') as fake_robots_txt:
                mock_get.return_value = FakeResponse()
                mock_get.return_value.text = fake_robots_txt.read()
                test_crawler = Crawler(
                    'https://a/',
                    [''], {})
                test_crawler.fill_disallow_urls(URL('https://a/'))
                self.assertEqual({re.compile('https://a/b.+', re.IGNORECASE)},
                                 test_crawler.disallow_urls)

    def test_update_parents(self):
        with patch.object(Crawler, 'get_html') as mock_get_html:
            mock_get_html.return_value = '<a href=http://a/c/></a>' \
                                         '<a href=http://a/b/></a>'
            with patch.object(Crawler, 'write_html') as mock_write_html:
                mock_write_html.return_value = None
            test_crawler = Crawler(
                'http://a',
                [''], {}, max_urls_count=3)
            test_result = test_crawler.crawl()
            for page in test_result:
                if page.parent:
                    self.assertEqual(page.parent,
                                     Page(URL('http://a'),
                                          test_crawler.origin_directory))


if __name__ == '__main__':
    unittest.main()
