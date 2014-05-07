#coding: utf-8

from django.contrib.auth.models import User

from apps.contents.constants import *
from apps.films.constants import *
from apps.contents.models import *
from apps.films.models import *

import factory
import datetime


class FilmFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Films
    FACTORY_DJANGO_GET_OR_CREATE = ('name',)
    name = factory.Sequence(lambda n: u'Фильм{0}'.format(n))
    type = APP_FILM_FULL_FILM
    release_date = datetime.date(2014, 3, 21)
    description = u'Боевик'
    name_orig = factory.Sequence(lambda n: u'Film{0}'.format(n))

    @factory.post_generation
    def genres(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for genre in extracted:
                self.genres.add(genre)

    @factory.post_generation
    def countries(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for country in extracted:
                self.countries.add(country)


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda q: u'name{0}'.format(q))
    password = factory.Sequence(lambda q: u'pass{0}'.format(q))


class ContentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Contents
    name = factory.SelfAttribute('film.name')
    film = factory.SubFactory(FilmFactory)
    release_date = factory.SelfAttribute('film.release_date')
    viewer_cnt = 0
    viewer_lastweek_cnt = 0
    viewer_lastmonth_cnt = 0


class LocationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Locations
    content = factory.SubFactory(ContentFactory)
    type = APP_CONTENTS_ONLINE_CINEMA
    lang = u'eng'
    price = float(0)
    price_type = APP_CONTENTS_PRICE_TYPE_FREE
    url_view = u'http://www.megogo.net/item/Red.html'
    quality = u''
    subtitles = u''


class GenreFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Genres
    name = factory.Sequence(lambda b: u'Жанр{0}'.format(b))
    description = factory.Sequence(lambda b: u'Описание Жанра_{0}'.format(b))


class CityFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Cities


class PersonFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Persons
    # city = factory.SubFactory(CityFactory)
    name = factory.Sequence(lambda u: u'Персона{0}'.format(u))
    name_orig = factory.Sequence(lambda u: u'Person{0}'.format(u))
    bio = u'Биография'
    photo = u''


class PersonsFilmFactory(factory.DjangoModelFactory):
    FACTORY_FOR = PersonsFilms
    film = factory.SubFactory(FilmFactory)
    person = factory.SubFactory(PersonFactory)
    p_type = APP_PERSON_ACTOR


class CommentsFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Comments
    user = factory.SubFactory(UserFactory)
    content = factory.SubFactory(ContentFactory)
    text = factory.Sequence(lambda x: u'Comment{0}'.format(x))


class FilmsExtrasFactory(factory.DjangoModelFactory):
    FACTORY_FOR = FilmExtras
    photo = factory.django.ImageField(filename=u'the_test_file.jpg')
    film = factory.SubFactory(FilmFactory)
    type = APP_FILM_TYPE_ADDITIONAL_MATERIAL_POSTER
    name = factory.Sequence(lambda v: u'Постер{0}'.format(v))
    name_orig = factory.Sequence(lambda v: u'Poster{0}'.format(v))
    description = factory.Sequence(lambda v: u'Описание{0}'.format(v))


class CountriesFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Countries
    name = factory.Sequence(lambda h: u'Страна{0}'.format(h))
    name_orig = factory.Sequence(lambda h: u'Country{0}'.format(h))


class UsersFilmsFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UsersFilms
    user = factory.SubFactory(UserFactory)
    film = factory.SubFactory(FilmFactory)
    status = APP_USERFILM_STATUS_UNDEF