# coding: utf-8
""" Command to crawler sites"""
from crawler.zoomby_ru.loader import ZOOMBY_Loader
from crawler.zoomby_ru.parsers import ParseFilm

from django.utils import timezone
from django.core.management.base import BaseCommand
from optparse import make_option

from apps.films.models import Films, Seasons
from apps.contents.models import Contents, Locations
from apps.contents.constants import *
from crawler.ivi_ru.loader import IVI_Loader
from crawler.ivi_ru.parsers import ParseFilmPage
from crawler.now_ru.loader import NOW_Loader
from crawler.now_ru.parsers import ParseNowFilmPage
from crawler.megogo_net.loader import MEGOGO_Loader
from crawler.megogo_net.parsers import ParseMegogoFilm
from crawler.core.exceptions import *
from crawler.playfamily_dot_ru.loader import playfamily_loader
from crawler.playfamily_dot_ru.parser import PlayfamilyParser
from crawler.tvigle_ru.loader import TVIGLE_Loader
from crawler.tvigle_ru.parsers import ParseTvigleFilm
from requests.exceptions import ConnectionError
from apps.robots.constants import APP_ROBOTS_TRY_SITE_UNAVAILABLE, APP_ROBOTS_TRY_NO_SUCH_PAGE, \
    APP_ROBOTS_TRY_PARSE_ERROR
from apps.robots.models import RobotsTries, Robots

import re
from crawler import Robot
import json



# Список допустимых сайтов


# Словарь сайтов:
# louder: загрузчик страници
# parser: парсер страници фильма
sites_crawler = {
    'ivi_ru': {'loader': IVI_Loader,
               'parser': ParseFilmPage},
    'zoomby_ru': {'loader': ZOOMBY_Loader,
                  'parser': ParseFilm()},
    'megogo_net': {'loader': MEGOGO_Loader,
                   'parser': ParseMegogoFilm},
    'now_ru': {'loader': NOW_Loader,
               'parser': ParseNowFilmPage},
    'amediateka_ru': {'loader': None,
                      'parser': None},
    'playfamily_ru': {'loader': playfamily_loader,
                      'parser': PlayfamilyParser()},
    'tvigle_ru': {'loader': TVIGLE_Loader,
                  'parser': ParseTvigleFilm()}
}
sites = sites_crawler.keys()


def sane_dict(film=None):
    '''
    Template for dict returned by parsers with sane defaults
    '''
    return {'film': film,
            'name': film.name,
            'name_orig': film.name_orig,
            'number': None,
            'description': film.description,
            'release_date': film.release_date,
            'series_cnt': None,
            'viewer_cnt': 0,
            'viewer_lastweek_cnt': 0,
            'viewer_lastmonth_cnt': 0,
            'price': 0,
            'price_type': APP_CONTENTS_PRICE_TYPE_FREE,
            'url_view': '',
            'quality': '',
            'subtitles': '',
            'url_source': ''
            }


def get_content(film, kwargs):
    '''
    Finds or creates content with this film.

    If there are

    number,release_data,description in kwargs then Contents
    object will be created with these defaults
    '''
    # Getting all content with this film
    contents = Contents.objects.filter(film=film)

    if 'number' in kwargs:
        season_num = kwargs['number']
    else:
        season_num = None

    if 'release_date' in kwargs:
        release_date = kwargs['release_date']
    else:
        release_date = None

    if 'description' in kwargs:
        description = kwargs['description']
    else:
        description = None

    if len(contents) == 0:
        #If there is no such content just creating one with meaningfull defaults

        if not season_num is None:
            raise NameError("Variant with new TV series not in db not implemented")
        content = Contents(film=film, name=film.name, name_orig=film.name_orig,
                           description=description,
                           release_date=film.release_date,
                           viewer_cnt=0,
                           viewer_lastweek_cnt=0,
                           viewer_lastmonth_cnt=0)
        content.save()
        return content

    else:
        if season_num is None:
            content = contents[0]
        else:
            content = next((c for c in contents if c.season.number == season_num), None)

            if content is None:

                precontent = contents[0]
                if release_date is None:
                    print "Assigned release date for new content based on release date for the film %d" %   film.pk
                    release_date = film.release_date

                if 'series_cnt' in kwargs:
                    series_cnt = kwargs['series_cnt']
                else:
                    print "Assigned new series count in season to number of series in previous season for season %d for film %d" % ( season_num, film.pk)
                    series_cnt = precontent.season.series_cnt

                season = Seasons(film=film, release_date=release_date,
                                 series_cnt=series_cnt, description=description,
                                 number=season_num)
                content = Contents(film=film, name=precontent.name,
                                   name_orig=precontent.name_orig,
                                   description=description, number=season_num,
                                   release_date=release_date,
                                   viewer_cnt=kwargs['viewer_cnt'],
                                   season=season,
                                   viewer_lastweek_cnt=kwargs['viewer_cnt'],
                                   viewer_lastmonth_cnt=kwargs['viewer_cnt'])
                content.save()
        return content


def save_location(film, **kwargs):
    content = get_content(film, kwargs)
    location = Locations(content=content,
                         type=0,
                         url_view=kwargs['url_view'],
                         quality=kwargs['quality'],
                         subtitles=kwargs['subtitles'],
                         price=kwargs['price'],
                         price_type=kwargs['price_type'])
    location.save()


def launch_next_robot_try(site):
    '''
    This will launch next robot iteration according to its setting stored in db

    As of now it just processes one next film

    '''

    try:
        robot = Robots.objects.get(name=site)
    except Robots.DoesNotExist:
        print 'There is no such site in db'
        return

    params = json.loads(robot.state)
    start = params['start'] if 'start' in params else 1

    film_number = start + 1
    film_number = 53
    film = Films.objects.filter(pk=film_number)

    print film

    if not film:
        film_number = 1
        film = Films.objects.filter(pk=film_number)
        if not film:
            print "Empty films db"
            return
        print "Starting again"


    robot.last_start = timezone.now()
    robot.state = json.dumps({'start': film_number})
    robot.save()

    if RobotsTries.objects.filter(film=film, domain=site, outcome=APP_ROBOTS_TRY_NO_SUCH_PAGE):
        print "Skipping this film {} on that site {} as previous attempt was unsuccessful".format(film,site)

    try:

        robot = Robot(films=film, **sites_crawler[site])
        for data in robot.get_data(sane_dict):
            print "Trying to put data from %s for %s to db" % (site, str(data['film']))
            save_location(**data)

    except ConnectionError, ce:
        # Couldn't conect to server
        print "Connection error"
        m = re.match(".+host[=][']([^']+)['].+", ce.message.message)

        host = m.groups()[0]
        url = ce.message.url
        if host is None:
            host = 'unknown'

        robot_try = RobotsTries(domain=host,
                                url='http://' + host + url,
                                film=film[0],
                                outcome=APP_ROBOTS_TRY_SITE_UNAVAILABLE
                                )

        robot_try.save()

    except RetrievePageException, rexp:
        # Server responded but not 200
        print "RetrievePageException"
        if site is None:
            site = 'unknown'

        robot_try = RobotsTries(domain=site,
                                url=rexp.url,
                                film=film[0],
                                outcome=APP_ROBOTS_TRY_NO_SUCH_PAGE
                                )

        robot_try.save()

    except UnicodeDecodeError:
        print "Unicode error"
        if site is None:
            site = 'unknown'

        robot_try = RobotsTries(domain=site,
                                film=film[0],
                                outcome=APP_ROBOTS_TRY_PARSE_ERROR
                                )

        robot_try.save()
    except NoSuchFilm as e:
        robot_try = RobotsTries(domain=site,
                                film=e.film,
                                outcome=APP_ROBOTS_TRY_NO_SUCH_PAGE)

        robot_try.save()
    '''
    except Exception, e:
        print "Unknown exception %s", str(e)
        # Most likely parsing error
        if site is None:
            site = 'unknown'

        robot_try = RobotsTries(domain=site,
                                film=film[0],
                                outcome=APP_ROBOTS_TRY_PARSE_ERROR
                                )

        robot_try.save()
    '''