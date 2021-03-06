
from apps.films.models import Films
from bs4 import BeautifulSoup
from crawler.locations_robot_corrector import LocationRobotsCorrector
from crawler.locations_saver import save_location_to_locs_dict, save_existed_location_to_locs_dict
from crawler.tasks.locrobots_logging import fill_log_table_for_not_schema_corresponded_robots
from crawler.tasks.test_robots_ban import MultiLocationRobotsBunCheck
from crawler.utils.locations_utils import save_location, sane_dict
from apps.contents.constants import *
from crawler.tor import simple_tor_get_page
import string


class ViaplayRobot(object):
    def __init__(self):
        self.price = float(395)
        self.price_type = APP_CONTENTS_PRICE_TYPE_SUBSCRIPTION

    def get_data(self):
        all_film_url = 'http://viaplay.ru/filmy/vse/5/alphabetical'
        locations = {
            'info': [],
            'type': 'viaplay'
                }
        content = simple_tor_get_page(all_film_url)
        soup_films = BeautifulSoup(content).find('ul', {'class': 'atoz-list'}).li.ul.find_all('li')
        films = Films.objects.values('name', 'id')
        for li_film in soup_films:
            for film in films:
                if li_film.a.text.lower().strip().encode('utf-8').translate(None, string.punctuation) == film['name'].lower().strip().encode('utf-8').translate(None, string.punctuation):
                    link = 'http://viaplay.ru' + li_film.a.get('href')
                    film_query_set = Films.objects.filter(id=film['id'])
                    for obj in film_query_set:
                        d = self.film_dict(obj, link)

                        one_loc_res = save_location(**d)
                        save_existed_location_to_locs_dict(locations, one_loc_res)
                    break
        fill_log_table_for_not_schema_corresponded_robots(locations)
        robot_is_banned = MultiLocationRobotsBunCheck.is_result_looks_like_robot_banned(locations)
        if not robot_is_banned:
            LocationRobotsCorrector.correct_locations(locations, 'viaplay')
        return locations

    def film_dict(self, film, film_link):
        resp_dict = sane_dict(film)
        resp_dict['url_view'] = film_link
        resp_dict['price_type'] = self.price_type
        resp_dict['price'] = self.price
        resp_dict['type'] = 'viaplay'
        return resp_dict