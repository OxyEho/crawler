import unittest
from unittest.mock import patch
from crawler.crawler import Crawler


class TestsCrawler(unittest.TestCase):
    def test_crawler_zero_result(self):
        with patch.object(Crawler, 'get_html') as mock_get_html:
            mock_get_html.return_value = '<a href=https://scala1.html></a>'
            with patch.object(Crawler, 'write_html') as mock_write_html:
                mock_write_html.return_value = None
                test_crawler = Crawler('https://docs.scala-lang.org/ru/tour/tour-of-scala.html', ['psina'], {}, 2)
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
                test_crawler = Crawler('https://docs.scala-lang.org/ru/tour/tour-of-scala.html', ['scala'], {})
                test_result = test_crawler.crawl()
                self.assertEqual(len(test_result), 10)

    def test_searcher_with_seen_urls(self):
        with patch.object(Crawler, 'get_html') as mock_get_html:
            mock_get_html.return_value = '<a href=http://scala-lang.org></a>' \
                                         '<a href=https://scala11.html></a>'
            with patch.object(Crawler, 'write_html') as mock_write_html:
                mock_write_html.return_value = None
                test_crawler = Crawler('https://docs.scala-lang.org/ru/tour/tour-of-scala.html', ['scala'], {}, 2)
                test_crawler.seen_urls.add('http://scala-lang.org')
                test_result = test_crawler.crawl()
                assert 'http://scala-lang.org' not in test_result

    def test_searcher_with_two_seen_urls(self):
        with patch.object(Crawler, 'get_html') as mock_get_html:
            mock_get_html.return_value = '<a href=http://scala-lang.org></a>' \
                                         '<a href=https://scala11.html></a>' \
                                         '<a href=https://www.scala-lang.org/download/></a>' \
                                         '<a href=https://scala12.html></a>' \
                                         '<a href=https://scala13.html></a>'
            with patch.object(Crawler, 'write_html') as mock_write_html:
                mock_write_html.return_value = None
                test_crawler = Crawler('https://docs.scala-lang.org/ru/tour/tour-of-scala.html', ['scala'], {}, 4)
                test_crawler.seen_urls.add('http://scala-lang.org')
                test_crawler.seen_urls.add('https://www.scala-lang.org/download/')
                test_result = test_crawler.crawl()
                assert 'http://scala-lang.org' not in test_result and \
                       'https://www.scala-lang.org/download/' not in test_result


if __name__ == '__main__':
    unittest.main()
