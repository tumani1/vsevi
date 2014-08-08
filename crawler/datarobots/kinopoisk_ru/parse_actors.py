# coding: utf-8

import os
from bs4 import BeautifulSoup
from apps.films.models import Persons, PersonsFilms, Films
from crawler.constants import PAGE_ARCHIVE
from crawler.tasks.person_task import update_kinopoisk_persone
from crawler.tor import simple_tor_get_page
from django.core.exceptions import ObjectDoesNotExist
from apps.films.constants import APP_PERSON_ACTOR, APP_PERSON_DIRECTOR, APP_PERSON_PRODUCER, APP_PERSON_SCRIPTWRITER


__author__ = 'vladimir'


class PersoneParser(object):
    def __init__(self, data):
        pass

    @staticmethod
    def acquire_page(page_id):
        if not os.path.exists(PAGE_ARCHIVE):
            os.mkdir(PAGE_ARCHIVE)

        dump_path = os.path.join(PAGE_ARCHIVE,str(page_id))
        page_dump = ''
        if os.path.exists(dump_path):
            with open(dump_path) as fd:
                page_dump = fd.read().decode('utf-8')

        if not page_dump:
            url =u"http://www.kinopoisk.ru/film/%d/cast/" % page_id
            res = simple_tor_get_page(url, tor_flag=True)
            page_dump = res.decode('cp1251')
            with open(dump_path, 'w') as fdw:
                fdw.write(page_dump.encode('utf-8'))

        return page_dump

    @staticmethod
    def is_persone_exists(kinopoisk_id):
        try:
            Persons.objects.get(kinopoisk_id = kinopoisk_id)
            return 1
        except ObjectDoesNotExist:
            return 0

    @staticmethod
    def detect_type_of_persone(div):
        pers_type = 0
        if div.text == u"Режиссеры":
            pers_type = APP_PERSON_DIRECTOR
        if div.text == u"Актеры":
            pers_type = APP_PERSON_ACTOR

        if div.text == u"Продюсеры":
            pers_type = APP_PERSON_PRODUCER

        if div.text == u"Сценаристы":
            pers_type = APP_PERSON_SCRIPTWRITER
        return pers_type

    @staticmethod
    def get_persone_id(div):
        photo_div = div.find('div',{ "class" : "photo" })
        href = photo_div.find('a').get('href')
        id = href.split('/')[2]
        return id

    @staticmethod
    def get_persone_name(div):
        photo_div = div.find('div',{ "class" : "name" })
        a = photo_div.find('a')
        name = a.contents[0]
        return name

    @staticmethod
    def get_persons_films(film, person, pers_type):
        person_film = PersonsFilms.objects.get(film=film, person=person, p_type=pers_type)
        if not person_film:
            print u"Adding link for film {} and person {}".format(film, person)
            person_film = PersonsFilms(person=person, film=film, p_type=pers_type)
            person_film.save()
        return person_film

    @staticmethod
    def get_person(name, kinopoisk_id):
        person = Persons.objects.get(kinopoisk_id=kinopoisk_id)
        if not person:
            person = Persons(name=name, photo='', kinopoisk_id=kinopoisk_id)
            person.save()
            print u'Added Person {}'.format(name)
        return person

    @staticmethod
    def update_persons_films_with_indexes(page_dump, film_id):
        try:
            film = Films.objects.get(kinopoisk_id=film_id)
            soup = BeautifulSoup(page_dump)
            div_wrap = soup.find("div", "block_left")
            index = 0
            pers_type = 0
            old_pers_type = 0
            for div in div_wrap.findAll('div'):
                actor_info_div = div.find('div', {"class": "actorInfo"})
                if not actor_info_div:
                    if not div.get("class"):
                        pers_type = PersoneParser.detect_type_of_persone(div)
                else:
                    if pers_type == 0:
                        continue
                    pers_id = PersoneParser.get_persone_id(actor_info_div)
                    pers_name = PersoneParser.get_persone_name(actor_info_div)
                    if old_pers_type == 0:
                        old_pers_type = pers_type
                    if pers_type == old_pers_type:
                        index += 1
                    else:
                        old_pers_type = pers_type
                        index = 1

                    persone = PersoneParser.get_person(name=pers_name, kinopoisk_id=pers_id)
                    update_kinopoisk_persone(pers_id)
                    person_for_film = PersoneParser.get_persons_films(film=film, person=persone, pers_type=pers_type)
                    person_for_film.p_index = index
                    person_for_film.p_type = pers_type
                    person_for_film.save()
                    print persone, person_for_film, person_for_film.p_type, person_for_film.p_index

        except Exception, e:
            import traceback
            traceback.print_exc()

