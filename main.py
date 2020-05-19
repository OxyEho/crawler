import re
import argparse
from crawler.crawler import Crawler


def main():
    # arguments_parser = argparse.ArgumentParser(description='Urls_finder')
    # arguments_parser.add_argument('start_url', type=str, help='The point of initial searching')
    # arguments_parser.add_argument('request', nargs='*', type=str, help='Search request')
    # arguments_parser.add_argument('--wildcard', nargs='*', type=str, default='', help='White domains')
    # arguments_parser.add_argument('-d', type=int, default=10, help='Maximum number of pages visited')
    # arguments_parser.add_argument('-f', type=str, default='log', help='Directory for downloaded pages')
    # args = arguments_parser.parse_args()
    # request = args.request
    # start_url = args.start_url
    # max_count_urls = args.d
    # white_domains = []
    # directory_for_download = args.f
    # for domain in args.wildcard:
    #     if domain.startswith('*'):
    #         white_domains.append(re.compile(fr'[^.]+.{domain[1::]}'))
    #     else:
    #         white_domains.append(domain)
    # crawler = Crawler(start_url, request, white_domains, max_count_urls, directory_for_download)
    crawler = Crawler('https://habr.com/ru/top/', [''], {}, 10, 'log')
    result = crawler.crawl()
    for link in result:
        print(link)
    print('Program is completed')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Program is completed')
