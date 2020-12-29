import unittest
from unittest.mock import patch
from crawler.crawler import Crawler
from crawler.parser import Parser


class TestsHtml(unittest.TestCase):
    def test_get_html_with_no_html(self):
        with patch.object(Crawler, 'get_html') as mock_get_html:
            mock_get_html.return_value = None
            crawler = Crawler('https://vcsacsavsdsdk.com/feed/', ['a'], {})
            test_result = crawler.get_html('https://vcsacsavsdsdk.com/feed/')
        self.assertIsNone(test_result)

    def test_get_url_with_not_url(self):
        with open('test_.html', 'r') as test:
            text = test.read()
            test_url = Parser('https://t/')
            self.assertEqual(len(test_url.get_urls(text)), 0)

    def test_get_url_with_urls(self):
        with open('test.html', 'r') as test:
            text = test.read()
            test_url = Parser('https://t/')
            self.assertEqual(len(test_url.get_urls(text)), 4)


if __name__ == '__main__':
    unittest.main()
