import re
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from crawler.crawler import Crawler


def show_graph(pages):
    graph = nx.Graph()
    for page in pages:
        graph.add_node(page.url)
        if page.parent is not None:
            graph.add_edge(page.parent.url, page.url)
    nx.draw(graph,
            node_color='red',
            node_size=1000,
            with_labels=True,
            alpha=0.6)


if __name__ == '__main__':
    try:
        arguments_parser = argparse.ArgumentParser(description='Urls_finder')
        arguments_parser.add_argument('start_url', type=str,
                                      help='The point of initial searching')
        arguments_parser.add_argument('request', nargs='*', default=[''],
                                      help='Search request')
        arguments_parser.add_argument('--wildcard', nargs='*', type=str,
                                      default='', help='White domains')
        arguments_parser.add_argument('-d', type=int, default=10,
                                      help='Maximum number of pages visited')
        arguments_parser.add_argument('-f', type=str, default='log',
                                      help='Directory for downloaded pages')
        arguments_parser.add_argument('-g', action='store_true',
                                      help='Show graph')
        arguments_parser.add_argument('-w', action='store_true',
                                      help='Save founded pages')
        args = arguments_parser.parse_args()
        white_domains = []
        for domain in args.wildcard:
            if domain.startswith('*'):
                white_domains.append(re.compile(fr'[^.]+.{domain[1::]}'))
            else:
                white_domains.append(domain)
        crawler = Crawler(args.start_url, args.request, white_domains, args.d,
                          args.f, args.w)
        result = crawler.crawl()
        if args.g:
            show_graph(result)
        for link in result:
            print(link.url)
        print('Program is completed')
        plt.show()
    except KeyboardInterrupt:
        print('Program is completed')