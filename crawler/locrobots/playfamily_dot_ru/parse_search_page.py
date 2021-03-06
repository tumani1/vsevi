# coding: utf-8
'''
Module for parsing search pages of playfamily.ru
'''


from crawler.playfamily_dot_ru.utils import rub_to_int
import urllib
from bs4 import BeautifulSoup


SEARCH_URL = u'http://playfamily.ru/search?{}'


def form_search_url(search_term):
    '''
    Generate search url for search term for playfamily.ru

    '''
    print search_term,type
    return SEARCH_URL.format(urllib.urlencode({'q':search_term.encode('utf-8')}))


def parse_search_page(html):
    '''
    Extract names, links to pages, and prices for
    movies from BeautifuSoup of search page from
    playfamily.ru
    '''

    page_soup =BeautifulSoup(html)
    link_price_tags = [(td.find('a'),
                        td.parent.select('li.movie-buy'))
                       for td in
                       page_soup.select('td.sr-movie.table-name')]
    name_links_price = [(l.text.strip(),
                          l.attrs['href'],
                          rub_to_int(
                              p.find('a').text.strip()
                          ))
                         for l, p in link_price_tags]

    return name_links_price






