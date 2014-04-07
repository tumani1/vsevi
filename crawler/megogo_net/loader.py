from crawler.core.exceptions import NoSuchFilm
import requests
import parsers
import urllib
from ..core import BaseLoader

HOST = 'www.megogo.net/ru'
URL_SEARCH = 'searchhint'
URL_LOAD = ''

class MEGOGO_Loader(BaseLoader):
    def __init__(self,  film, host=HOST, url_load=URL_LOAD):
        super(MEGOGO_Loader, self).__init__(film, host, url_load)
        self.search_url = URL_SEARCH
        self.params = {'lang': 'ru', 'q': self.film.name}

    def get_url(self, load_function):
        url = "http://%s/%s" % (self.host, self.search_url, )
        response = load_function(url, params=self.params, cache=False)
        film = parsers.parse_search(response, self.film.name)
        if film is None:
            raise NoSuchFilm(self.film)
        self.url_load = film['view_link']
        return self.url_load