import re
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from crawler.crawler import Crawler


def main():
    arguments_parser = argparse.ArgumentParser(description='Urls_finder')
    arguments_parser.add_argument('start_url', type=str, help='The point of initial searching')
    arguments_parser.add_argument('request', nargs='*', default=[''], help='Search request')
    arguments_parser.add_argument('--wildcard', nargs='*', type=str, default='', help='White domains')
    arguments_parser.add_argument('-d', type=int, default=10, help='Maximum number of pages visited')
    arguments_parser.add_argument('-f', type=str, default='log', help='Directory for downloaded pages')
    arguments_parser.add_argument('-g', type=int, default=1,
                                  help='Do not show the graph of searching if 0 else show the graph')
    args = arguments_parser.parse_args()
    request = args.request
    start_url = args.start_url
    max_count_urls = args.d
    white_domains = []
    directory_for_download = args.f
    for domain in args.wildcard:
        if domain.startswith('*'):
            white_domains.append(re.compile(fr'[^.]+.{domain[1::]}'))
        else:
            white_domains.append(domain)
    crawler = Crawler(start_url, request, white_domains, max_count_urls, directory_for_download)
    # crawler = Crawler('https://habr.com/ru/top/', [''], {}, 10, 'log')
    result = crawler.crawl()
    if args.g:
        show_graph(result)
    for link in result:
        print(link.url)
    print('Program is completed')
    plt.show()


def show_graph(pages):
    graph = nx.Graph()
    for page in pages:
        graph.add_node(page.url)
        if page.parent is not None:
            graph.add_edge(page.parent.url, page.url)
    nx.draw(graph,
            node_color='red',
            node_size=100,
            with_labels=False,
            alpha=0.6)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Program is completed')
