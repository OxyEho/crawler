import unittest
from crawler.crawler import Crawler
from crawler.parser import Parser


class TestsHtml(unittest.TestCase):
    def test_get_html_with_no_html(self):
        test_result = Crawler.get_html('https://vcsacsavsdsdk.com/feed')
        self.assertIsNone(test_result)

    def test_get_url_with_not_url(self):
        with open('test_.html', 'r') as test:
            text = test.read()
            test_url = Parser('https://t')
            self.assertEqual(len(test_url.get_urls(text)), 0)

    def test_get_url_with_urls(self):
        with open('test.html', 'r') as test:
            text = test.read()
            test_url = Parser('https://t')
            self.assertEqual(len(test_url.get_urls(text)), 4)


if __name__ == '__main__':
    unittest.main()
