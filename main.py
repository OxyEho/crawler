import re
import argparse
from crawler.crawler import Crawler


def main():
    arguments_parser = argparse.ArgumentParser(description='Urls_finder')
    arguments_parser.add_argument('start_url', type=str, help='The point of initial searching')
    arguments_parser.add_argument('request', nargs='*', type=str, help='Search request')
    arguments_parser.add_argument('--wildcard', nargs='*', type=str, default='', help='White domains')
    arguments_parser.add_argument('-d', type=int, default=10, help='Maximum number of pages visited')
    args = arguments_parser.parse_args()
    request = args.request
    start_url = args.start_url
    max_count_urls = args.d
    white_domains = []
    for domain in args.wildcard:
        if domain.startswith('*'):
            reg_exp_domain = f'[^.]+{domain[1::]}'
            white_domains.append(re.compile(r'{}'.format(reg_exp_domain)))
        else:
            white_domains.append(domain)
    crawler = Crawler(start_url, request, white_domains, max_count_urls)
    crawler.searcher()
    print('Program is completed')
    exit()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Program is completed')
