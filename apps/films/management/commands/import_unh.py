# coding: utf-8

import os, csv, re
from datetime import datetime
import codecs
import chardet
import datetime
import warnings

from django.db import DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import LabelCommand, BaseCommand, CommandError
from optparse import make_option
from django.db import models
from django.contrib.contenttypes.models import ContentType

from apps.films.constants import *
from apps.films.models import Films, Genres, Countries, PersonsFilms, FilmExtras
from apps.users.models import Persons

class Command(BaseCommand):
    def __init__(self):
        super(Command, self).__init__()
        self.charset = ''

    def handle(self, *args, **options):
        filename =  args[0]
        if os.path.exists(filename):
            self.stdout.write('Start: Import from UNH CSV from %s' % filename)
            self.import_file( filename)
        else:
            raise Exception('File %s not found' % filename)

    def import_file(self, filename):
        self.stdout.write('Run import -  %s' % filename)
        data = self.__csvfile(filename)
        headers = data[0]
        counter = 0

        for row in data[1:]:
            item = dict(zip(headers, row)) if (len(headers) <= len(row)) else dict(map(None, headers, row))
            if self.insert_item(item):
                counter += 1
            if ((counter % 100) == 0):
                self.stdout.write('Inserted  {0} items'.format(counter))

        self.stdout.write('Inserted  {0} items'.format(counter))

    def charset_csv_reader(self, csv_data, dialect=csv.excel,
                           charset='utf-8', **kwargs):
        csv_reader = csv.reader(self.charset_encoder(csv_data, charset),
                                dialect=dialect, delimiter=';', **kwargs)
        for row in csv_reader:
            yield [unicode(cell, charset) for cell in row]

    def charset_encoder(self, csv_data, charset='utf-8'):
        for line in csv_data:
            yield line.encode(charset)

    def __csvfile(self, datafile):
        self.charset='utf-8'
        csvfile = codecs.open(datafile, 'r', self.charset)
        return list(self.charset_csv_reader(csv_data=csvfile,
                                            charset=self.charset))

    def insert_item(self, data):
        try:
            attributes = {
                'name': self.film_name(data),
                'name_orig': self.film_name_orig(data),
                'description': self.film_description(data),
                'ftype': APP_FILM_FULL_FILM,
                'kinopoisk_id': data['id_kinopoisk'],
                'frelease_date': self.date_or_now(data['release']),
                'rating_imdb': data['vote_imdb'],
                'rating_imdb_cnt': data['vote_imdb_number'],
                'fduration': self.null_to_none(data['length'])
            }

            film = Films(**attributes)
            film.save()
            film.genres = self.get_genres(genres=data['genre_ru'])
            film.countries = self.get_countries(countries=u'Флатландию')
            film.save()
            self.save_trailer(film, data)
            self.save_actors(film, data)
            self.save_director(film, data)

            return True
        except Exception as ex:
            print('========== {0} =='.format(ex.message))
            print('==============================================')
            print(data.__repr__())
            return False
    def null_to_none(self, value = None):
        if value is None:
            return None
        if value.lower() == 'null':
            return None
        return value

    def film_description(self, data):
        list_desc = [data['description_ru'], data['description_eng']]
        lists = filter(lambda v: ((not v is None) and (v.lower() != u'null')), list_desc)
        return lists[0] if lists else ''

    def film_name(self, data):
        list_names = [data['title_ru'], data['title_eng'], data['title_orig']]
        lists = filter(lambda v: ((not v is None) and (v.lower() != u'null')), list_names)
        return lists[0] if lists else ''

    def film_name_orig(self, data):
        list_names = [data['title_orig'], data['title_eng']]
        lists = filter(lambda v: ((not v is None) and (v.lower() != u'null')), list_names)
        return lists[0] if lists else ''

    def save_trailer(self, film, data = None):
        if data is None:
            return True
        trailer_youtube_id = data['trailer_youtube']
        if (trailer_youtube_id is None) or (trailer_youtube_id.lower() == 'null'):
            return True

        youtube_url = "https://www.youtube.com/watch?v=" + trailer_youtube_id
        try:
            traler = FilmExtras.get(url=youtube_url,
                                    etype=APP_FILM_TYPE_ADDITIONAL_MATERIAL_TRAILER)
        except:
            traler = FilmExtras(film=film,
                                name=film.name,
                                name_orig=film.name_orig,
                                url=youtube_url,
                                etype=APP_FILM_TYPE_ADDITIONAL_MATERIAL_TRAILER)
            traler.save()
        return True

    # person_data[0] - ru name
    # person_data[1] - eng name
    #
    def get_person(self, person_data):
        try:
            person_model = Persons.objects.get(name=person_data[0].strip())
        except:
            person_model = Persons(name=person_data[0].strip(),
                                   name_orig=person_data[1].strip())
            person_model.save()
        return person_model

    def save_actors(self, film, data = None):
        actors_ru_names = self.compact_list(data['actors_ru'].split(','))
        actors_eng_names = self.compact_list(data['actors_eng'].split(','))
        actors_names = zip(actors_ru_names, actors_eng_names)
        for actor_name in actors_names:
            actor = self.get_person(actor_name)
            person_film = PersonsFilms(film=film,
                                       person=actor,
                                       p_type=APP_PERSON_ACTOR)
            person_film.save()
        return True

    def save_director(self, film, data = None):
        director_ru_names = self.compact_list(data['director_ru'].split(','))
        director_eng_names = self.compact_list(data['director_eng'].split(','))
        directors_names = zip(director_ru_names, director_eng_names)
        for director_name in directors_names:
            director = self.get_person(director_name)
            person_film = PersonsFilms(film=film,
                                       person=director,
                                       p_type=APP_PERSON_DIRECTOR)
            person_film.save()
        return True

    def compact_list(self, list = []):
        return [ el for el in list if (not el is None) and (el.lower() != 'null')]

    def date_or_now(self, date = None):
        if date is None:
            return datetime.datetime.now()
        if self.is_null(date):
            return datetime.datetime.now()
        return datetime.datetime.strptime(date, '%Y-%m-%d')

    def is_null(self, value = None):
        if value is None:
            return true
        return value.lower() == u'NULL'.lower()

    def get_genres(self, genres = None):
        if genres is None:
            return []
        genre_names = map(lambda v: v.strip(), genres.split(','))
        genre_models = []
        for genre_name in genre_names:
            try:
                genre_model = Genres.objects.get(name=genre_name)
            except:
                genre_model = Genres(name=genre_name)
                genre_model.save()

            genre_models.append(genre_model)

        return genre_models

    def get_countries(self, countries = None):
        if countries is None:
            return []
        country_names = map(lambda v: v.strip(), countries.split(','))
        country_models = []
        for country_name in country_names:
            try:
                country_model = Countries.objects.get(name=country_name)
            except:
                country_model = Countries(name=country_name)
                country_model.save()

            country_models.append(country_model)

        return country_models
