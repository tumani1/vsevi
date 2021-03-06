import requests
import json
import re
from crawler.locations_robot_corrector import LocationRobotsCorrector
from crawler.locations_saver import save_location_to_locs_dict, save_existed_location_to_locs_dict
from crawler.tasks.locrobots_logging import fill_log_table_for_not_schema_corresponded_robots
from crawler.tasks.test_robots_ban import MultiLocationRobotsBunCheck

from crawler.utils.locations_utils import sane_dict, save_location
from apps.contents.constants import APP_CONTENTS_PRICE_TYPE_FREE, APP_CONTENTS_PRICE_TYPE_PAY
from apps.films.models import Films

URL_TEMPLATE = "http://drugoekino.ru/core/films?sub=0&free=0&rus=0&keyword=&order=3&curPos={}&Mood1=0&Mood2=0&Mood3=0&Mood4=0&Mood5=0&Mood6=0&Mood7=0&Mood8=0&Mood9=0"

ROOT_URL = "http://drugoekino.ru"
STEP = 6

def films_data():

    try:
        current = 1
        first_request = requests.post(URL_TEMPLATE.format(current))
        first_data = first_request.json()

        for f in first_data['films']:
            yield f

        limit = int(first_data['listing']['total'])
        print "Found {} films".format(limit)
        while current + STEP < limit:
            current += STEP
            req = requests.post(URL_TEMPLATE.format(current))
            for f in req.json()['films']:
                yield f

    except Exception,e:
        import traceback
        traceback.print_exc()



def update_drugoe_kino_listing():

    locations = {
        'info': [],
        'type': 'drugoe_kino'
                }
    for fdict in films_data():
        try:
            film = Films.objects.get(name = fdict['Title_Rus'], release_date__year=fdict['Year'])
        except Films.DoesNotExist:
            try:
                if fdict['Title_Orig']:
                    film = Films.objects.get(name_orig = fdict['Title_Orig'], release_date__year=fdict['Year'])
                else:
                    film = None
            except Films.DoesNotExist:
                film = None

        except :
            import traceback
            traceback.print_exc()

        if film:
            sd = sane_dict(film)
            sd['type'] = 'drugoekino'
            sd['price'] = int(fdict["Price"]) if fdict["Price"] else 0
            if sd['price']:
                sd['price_type'] = APP_CONTENTS_PRICE_TYPE_PAY
            sd['url_view']= ROOT_URL + fdict['Link']
            try:
                sd['value']= re.match('/watch/film/film_(?P<value>\d+).html', fdict['Link']).groupdict()['value']
            except:
                import traceback
                traceback.print_exc()

            one_loc_res = save_location(**sd)
            save_existed_location_to_locs_dict(locations, one_loc_res)
    fill_log_table_for_not_schema_corresponded_robots(locations)
    robot_is_banned = MultiLocationRobotsBunCheck.is_result_looks_like_robot_banned(locations)
    if not robot_is_banned:
        LocationRobotsCorrector.correct_locations(locations, 'drugoekino')
    return locations