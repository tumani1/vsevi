# coding: utf-8
import os
import json
from crawler.locrobots import sites_crawler
from apps.films.models import Films
from crawler.core.exceptions import NoSuchFilm

saved_pages_directory = 'saved_pages'


def save_loaded_data_to_file(loaded_json_data, file_name, sub_dir_name):
    saved_file_name = file_name + '.json'
    try:
        if not os.path.exists(saved_pages_directory):
            os.makedirs(saved_pages_directory)
        site_dir = saved_pages_directory + '/' + sub_dir_name
        if not os.path.exists(site_dir):
            os.makedirs(site_dir)
        f = open(site_dir + '/' + saved_file_name, 'w')
        f.write(json.dumps(loaded_json_data))
        f.close()
    except Exception, e:
        print "Saving failed with error:", e.message
        return None
    return site_dir + '/' + saved_file_name


def load_and_save_film_page_from_site(site, film_id, url=None):
    saved_file_name = ''
    try:
        saved_file_name = None
        film = Films.objects.get(id=film_id)
    except Films.DoesNotExist:
        print "There is no film in db with such id"
        return None
    try:
        print "trying to load " + str(film_id) +" from:", site
        loaded_data = sites_crawler[site]['loader'](film).load(url=url) #загрузка страницы
        saved_file_name = save_loaded_data_to_file(loaded_data, 'film_id_' + str(film.id), site)
        print "loaded ok"
    except NoSuchFilm:
        print "no such film"
    except Exception, e:
        print "page loading failed", e.message
        return None
    return saved_file_name
