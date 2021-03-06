# coding: utf-8
import re
import os
import json
import warnings
from cgi import escape
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, timedelta
from random import randrange
from cStringIO import StringIO
from PIL import Image, ImageEnhance


from django.db import connection

from django.core.files import File
from django.core.cache import cache
from django.core.context_processors import csrf
from django.core.serializers.json import DjangoJSONEncoder
from django.template import Context
from django.views.generic import View
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from rest_framework import status


import apps.films.models as film_model
import apps.contents.models as content_model

import apps.films.models as film_model
from apps.films.api.serializers import vbFilm, vbComment, vbPerson

from apps.films.constants import APP_USERFILM_STATUS_PLAYLIST, APP_PERSON_ACTOR, \
    APP_PERSON_DIRECTOR, APP_PERSON_SCRIPTWRITER, APP_FILM_FULL_FILM, APP_USERFILM_STATUS_NOT_WATCH

from apps.films.api import SearchFilmsView
from apps.contents.models import Comments, Contents
from apps.films.forms import CommentForm
from apps.films.models import Films
from apps.users import Feed, SessionToken
from apps.users.constants import FILM_COMMENT

from utils.noderender import render_page
from utils.common import reindex_by
from utils.noderender import render_page
from utils.middlewares.local_thread import get_current_request


def get_new_namestring(namestring):
    m = re.match("(?P<pre>.+)v(?P<version>[0-9]+)[.]png", namestring)

    if m is None:
         filename = namestring + '_v1.png'
    else:
        d = m.groupdict()
        filename = '{:s}v{:d}.{:s}'.format(d['pre'], int(d['version']) + 1, 'png')

    return filename


def image_refresh(func):
    def wrapper(request):
        url = request.POST.get('image')
        m = re.match('.+[/]static[/]upload[/](?P<type>[^/]+)[/](?P<id>[0-9]+)', url)

        path = re.match('.+(?P<path>[/]static[/].+)', url)
        d = m.groupdict()

        if d['type'] == 'persons':
            p = film_model.Persons.objects.get(pk=int(d['id']))
        elif d['type'] == 'filmextras':
            p = film_model.FilmExtras.objects.get(pk=int(d['id']))
        else:
            warnings.warn("Unknown type {} of requests for image manipulation")

        im = Image.open('.' + path.groupdict()['path'])
        imc = func(d, im, request)

        imfile = StringIO()

        imc.save(imfile, "PNG")
        imfile.seek(0)

        p.photo.save(get_new_namestring(os.path.basename(path.groupdict()['path'])), File(imfile))
        return HttpResponse("OK")

    return wrapper


@image_refresh
def resize_image(d, im, request):
    x = int(request.POST.get('x'))
    y = int(request.POST.get('y'))
    x2 = int(request.POST.get('x2'))
    y2 = int(request.POST.get('y2'))
    imc = im.crop((x, y, x2, y2))

    return im


@image_refresh
def bri_con(d, im, request):
    br = request.POST.get('br')
    co = request.POST.get('co')
    bre = ImageEnhance.Brightness(im)

    imc = im
    if br:
        imc = bre.enhance(2*(int(br))/100.0)

    coe = ImageEnhance.Contrast(imc)
    if co:
        imc = coe.enhance(2*(int(co))/100.0)

    return imc


class IndexView(View):

    def get(self, *args, **kwargs):
        # Выбираем 4 новых фильма, у которых есть локации
        NEW_FILMS_CACHE_KEY = 'new_films'
        resp_dict_serialized = cache.get(NEW_FILMS_CACHE_KEY)
        # Расчитываем новинки, если их нет в кеше
        if resp_dict_serialized is None:
            o_film = film_model.Films.get_newest_films()

            # Фильмы показывались => ставим флаг просмотрено в true
            for film in o_film:
                film.was_shown = True
                film.save()

            # Сериализуем новинки и конвертируем результат в строку
            resp_dict_data = vbFilm(o_film, require_relation=False, extend=True, many=True).data
            resp_dict_serialized = json.dumps(resp_dict_data, cls=DjangoJSONEncoder)

            # Положим результат в кеш
            cache.set(NEW_FILMS_CACHE_KEY, resp_dict_serialized, 86400)

        else:
            resp_dict_data = json.loads(resp_dict_serialized)

        # Найдем relation для фильмов, если пользователь авторизован
        if self.request.user.is_authenticated():
            o_user = film_model.UsersFilms.objects.filter(
                user=self.request.user, film__in=[item['id'] for item in resp_dict_data]
            )
            o_user = reindex_by(o_user, 'film_id', True)

            for index, item in enumerate(resp_dict_data):
                if item['id'] in o_user:
                    resp_dict_data[index]['relation'] = o_user[item['id']].relation_for_vb_film

        # Топ комментариев к фильмам  пользователей
        comments = content_model.Comments.get_top_comments_with_rating(struct=True)

        # Выборка списка жанров из кеша, если есть
        genres_cache_key = film_model.Genres.get_cache_key()
        genres_data = cache.get(genres_cache_key)

        if genres_data is None:
            try:
                genres_data = list(film_model.Genres.get_grouped_genres())
                cache.set(genres_cache_key, genres_data, 86400)
            except:
                genres_data = []

        # Формируем ответ
        data = {
            'films_new': resp_dict_data,
            'filter_genres': genres_data,
            'comments': comments,
            'films': get_recommend_film(self.request),
        }

        return HttpResponse(render_page('index', data), status.HTTP_200_OK)


class PersonView(View):

    def get(self, *args, **kwargs):
        try:
            person = film_model.Persons.objects.get(pk=kwargs['resource_id'])
        except film_model.Persons.DoesNotExist:
            raise Http404

        crutch = vbPerson(person, extend=True).data

        # костыль, до починки парсинга этих данных роботом.
        if not crutch.get('birthdate', False):
            d1 = date(1960, 1, 1)
            d2 = date(1980, 12, 12)
            delta = d2 - d1
            delta = delta.days*24*60*60
            seconds = randrange(delta)
            birthdate = (d1 + timedelta(seconds=seconds))
            crutch['birthdate'] = birthdate.strftime('%d %B %Y')
            crutch['years_old'] = date.today().year - birthdate.year

        # Выбираем фильмографию
        pfs = film_model.PersonsFilms.objects.filter(person=person)[:12]
        crutch['filmography'] = vbFilm([pf.film for pf in pfs], many=True).data

        return HttpResponse(render_page('person', {'person': crutch}))


class FilmView(View):

    def get(self, *args, **kwargs):
        resp_dict = film_to_view(kwargs['film_id'], similar=True)

        # Trailer
        trailer = film_model.FilmExtras.get_trailer_by_film(kwargs['film_id'], first=True)
        if not trailer is None:
            resp_dict['trailer'] = trailer.url

        return HttpResponse(render_page('film', {'film': resp_dict}))


class CommentFilmView(View):

    def __get_object(self, film_id):
        """
        Return object Contents or Response object with 404 error
        """

        try:
            o_film = Films.objects.get(id=film_id)
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        try:
            o_content = Contents.objects.get(film=o_film.id)
        except Contents.DoesNotExist, e:
            try:
                o_content = Contents(
                    film=o_film, name=o_film.name, name_orig=o_film.name_orig,
                    description=o_film.description, release_date=o_film.release_date,
                    viewer_cnt=0, viewer_lastweek_cnt=0, viewer_lastmonth_cnt=0
                )
                o_content.save()
            except Exception, e:
                return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        except Contents.MultipleObjectsReturned, e:

            if o_film.type == APP_FILM_FULL_FILM:
                print "Found multiple contents for film id={}"
                first_content = Contents.objects.filter(film=o_film).order_by("id")[0]

                for comm in Comments.objects.filter(content__film=o_film).exclude(content__pk=first_content.id):
                    print comm.content.id
                    invalid_content = comm.content
                    comm.content = first_content
                    invalid_content.delete()
                    comm.save()
            else:
                o_content = Contents.objects.filter(film=o_film.id).all()[0]
            
        return o_content

    def post(self, request, film_id, format=None, *args, **kwargs):
        form = CommentForm(request.REQUEST)
        if form.is_valid():
            # Выбираем и проверяем, что фильм существует
            o_content = self.__get_object(int(film_id))
            user = SessionToken.objects.get(key=request.COOKIES['x-session']).user

            # Init data
            filter_ = {
                'user': user,
                'text': re.sub('\n+', '<br>', escape(form.cleaned_data['text'])),
                'content': o_content
            }

            o_com = Comments.objects.create(**filter_)
            Feed.objects.create(user=SessionToken.objects.get(key=request.COOKIES['x-session']).user, type=FILM_COMMENT, obj_id=o_com.id, child_obj_id=o_content.film_id)

            return HttpResponseRedirect('/films/{}'.format(film_id))

        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


class FilmPoster(View):

    def get(self, *args, **kwargs):
        try:
            film_id = self.kwargs['film_id']

            if 'size' in self.kwargs:
                size = self.kwargs['size']
                return HttpResponseRedirect('/static/upload/filmextras/{}/poster_{}.jpg'.format(film_id, size))
        except KeyError:
            return HttpResponseBadRequest()

        return HttpResponseRedirect('/static/upload/filmextras/{}/poster.jpg'.format(film_id))


class PlayListView(View):

    def get(self, *args, **kwargs):
        film_id = kwargs.get('film_id', 1)
        if self.request.user.is_authenticated():
            # Init data
            film_data = {}
            playlist = {'id': 0}
            film_id = int(film_id)

            # Выборка плейлиста
            playlist_data = film_model.Films.objects.\
                filter(uf_films_rel__user=self.request.user.id, uf_films_rel__status=APP_USERFILM_STATUS_PLAYLIST).\
                order_by('uf_films_rel__created')

            # Обработка плейлиста
            len_playlist = len(playlist_data)
            if len_playlist > 0:
                if film_id > len(playlist_data) or film_id < 1:
                    return redirect('playlist_film_view', film_id=1)

                def arrow_data(data, f_id):
                    return {'id': f_id, 'name': data.name}

                if film_id < len(playlist_data):
                    playlist['next'] = arrow_data(playlist_data[film_id], film_id+1)

                if film_id > 1:
                    playlist['previous'] = arrow_data(playlist_data[film_id-2], film_id-1)

                film = playlist_data[film_id-1]
                film_data = film_to_view(film.id)

            # Update playlist
            playlist.update({
                'id': film_id,
                'film': film_data,
                'total_cnt': len_playlist,
                'items': vbFilm(playlist_data, many=True).data,

                # Список рекомендуемых фильмов
                'films': get_recommend_film(self.request),
            })

            return HttpResponse(render_page('playlist', {'playlist': playlist, 'film': film_data}))

        return redirect('login_view')


class SearchView(View):

    def get(self, *args, **kwargs):
        # Устанавливаем ответ по умолчанию и вызываем сериализатор поиска
        resp_dict = {
            'films': [],
        }

        if self.request.REQUEST.get('text'):
            try:
                resp_dict['films'] = SearchFilmsView.as_view()(self.request, use_thread=True).data
                resp_dict['search_text'] = self.request.REQUEST.get('text')
            except Exception, e:
                pass

        return HttpResponse(render_page('search', resp_dict))


def test_view(request):
    c = Context({})
    c.update(csrf(request))

    return render_to_response('api_test.html', c)


def serialize_actors(actors_iterable):

    return [{'id': pf.person.id, 'name': pf.person.name, 'photo': pf.person.get_path_to_photo} for pf in actors_iterable]



def calc_actors(o_film):
    result = []
    filter = {
        'filter': {'pf_persons_rel__film': o_film.id},
        'offset': 0,
        'limit': 5,
    }

    try:
        enumerated_actors = film_model.PersonsFilms.objects.filter(film=o_film, p_type=APP_PERSON_ACTOR
        ).exclude(p_index=0).order_by('p_index')

        unenumerated_actors = film_model.PersonsFilms.objects.filter(film=o_film, p_type=APP_PERSON_ACTOR).filter(p_index=0)
        
        result = (serialize_actors(enumerated_actors) + serialize_actors(unenumerated_actors))[slice(filter['offset'], filter['limit'])]

    except Exception, e:
        print "Caught exception {} in calc_actors".format(e)

    return result


def calc_similar(film_id, actors, directors, genres, **kwargs):
    result = []
    list_films = []
    exclude_films = []
    cursor = connection.cursor()

    ############################################################################
    # Если авторизован, то список исключающих фильмов
    request = get_current_request()
    if request.user.is_authenticated():
        sql = """
        "films"."id" NOT IN (SELECT "users_films"."film_id" FROM "users_films"
        WHERE "users_films"."user_id" = %s AND ("users_films"."status" = %s OR
        "users_films"."rating" IS NOT NULL))
        """

        exclude_films = film_model.Films.objects.extra(
            where=[sql],
            params=[request.user.id, APP_USERFILM_STATUS_NOT_WATCH],
        ).values_list('id', flat=True)

        exclude_films = list(exclude_films)

    # Исключаем текущий фильм
    exclude_films.append(film_id)

    ############################################################################
    # 4 фильма по рейтингу от режисера и сценариста
    if len(directors):
        list_films = film_model.Films.objects.\
            filter(
                pf_films_rel__person__in=directors,
                pf_films_rel__p_type__in=[APP_PERSON_DIRECTOR, APP_PERSON_SCRIPTWRITER],
                type=APP_FILM_FULL_FILM
            ).exclude(id__in=exclude_films).\
            order_by('-rating_sort').\
            values_list('id', flat=True)[:4]

        list_films = list(list_films)

    ############################################################################
    # 4 фильма по рейтингу от актера
    if len(actors):
        sql = """
        SELECT t1.film_id FROM films AS t0 JOIN first_3_actor_by_film AS t1 ON t0.id=t1.film_id
        WHERE t0.type='{}' AND t1.person_id IN ({}) AND NOT (t0.id IN ({}))
        ORDER BY t0.rating_sort DESC LIMIT 4;
        """.format(APP_FILM_FULL_FILM,
            u','.join([str(i['id']) for i in actors]),
            u','.join([str(i) for i in set(list_films + exclude_films)])
        )

        # Исполнение запроса
        cursor.execute(sql)

        list_films += [row[0] for row in cursor.fetchall()]

    ############################################################################
    # 4 фильма по рейтингу от жанров
    if len(genres):
        sql = ""
        len_genres = len(genres)
        template = "SELECT films_id FROM films_genres where genres_id={}"

        for k, v in enumerate((i['id'] for i in genres), 1):
            sql += template.format(v)
            if k != len_genres:
                sql += " AND films_id IN ("

        if len_genres > 1:
            sql += ')' * (len_genres - 1)

        sql = """
        SELECT films.id FROM films WHERE films.id IN ({}) AND NOT (films.id IN ({}))
        ORDER BY films.rating_sort DESC LIMIT {};
        """.format(
            sql,
            ','.join([str(i) for i in set(list_films + exclude_films)]),
            12 - len(list_films)
        )

        cursor.execute(sql)

        list_films += [row[0] for row in cursor.fetchall()]

    ############################################################################
    # Финальная обработка

    # Закрытие курсора
    cursor.close()

    required_films = 12 - len(list_films)
    films_to_str = ','.join([str(i) for i in list_films])

    sql = ""
    if len(films_to_str):
        sql = "SELECT * FROM films WHERE films.id IN ({})".format(films_to_str)

    # Добираем фильмы, если необходимо
    if required_films:
        if len(films_to_str):
            sql += """ UNION (SELECT * FROM films WHERE films.id NOT IN ({})
             ORDER BY films.rating_sort DESC LIMIT {})
            """.format(films_to_str, required_films)
        else:
            sql = """SELECT * FROM films
            ORDER BY films.rating_sort DESC LIMIT {}""".format(required_films)

    ############################################################################
    # Преобразование данных
    try:
        result = vbFilm(film_model.Films.objects.raw(sql), many=True).data
    except Exception, e:
        print "Caught exception {} in calc_similar".format(e)

    return result


def calc_comments(o_film):
    try:
        content = content_model.Contents.objects.get(film=o_film.pk)
    except Exception, e:
        return []

    result_list = content_model.Comments.objects.filter(content=content.id).order_by('-created')[:5]
    try:
        result_list = vbComment(result_list, many=True).data
    except:
        result_list = []

    return result_list


def film_to_view(film_id, similar=False):
    o_film = film_model.Films.objects.filter(pk=film_id).prefetch_related('genres', 'countries')

    if not len(o_film):
        raise Http404

    o_film = o_film[0]
    resp_dict = vbFilm(o_film, extend=True)

    try:
        resp_dict = resp_dict.data
    except Exception, e:
        raise Http404

    resp_dict['actors'] = calc_actors(o_film)
    resp_dict['comments'] = calc_comments(o_film)

    # Выбираем рекомендуемые фильмы
    if similar:
        resp_dict['similar'] = calc_similar(film_id,
            actors=resp_dict['actors'][:3],
            genres=resp_dict['genres'][:3],
            directors=list(set(item['id'] for item in resp_dict['directors'] + resp_dict['scriptwriters'])),
        )

    return resp_dict


def kinopoisk_view(request, film_id, *args, **kwargs):
    # Проверяем, есть ли такой film_id в нашей базе данных
    # и что эта запись уникальна
    try:
        o_film = film_model.Films.objects.get(kinopoisk_id=film_id)
        return redirect('film_view', film_id=o_film.id)
    except Exception, e:
        pass

    return redirect('index_view')


def get_recommend_film(request):
    try:
        o_recommend = SearchFilmsView.as_view()(request, use_thread=True, recommend=True).data
        o_recommend = o_recommend['items']
    except Exception, e:
        o_recommend = []

    return o_recommend


class PersonsPhoto(View):

    def get(self, *args, **kwargs):
        try:
            person_id = self.kwargs['person_id']

            if 'size' in self.kwargs:
                size = self.kwargs['size']
                return HttpResponseRedirect('/static/upload/persons/{}/profile_{}.jpg'.format(person_id, size))
        except KeyError:
            return HttpResponseBadRequest()

        return HttpResponseRedirect('/static/upload/persons/{}/profile.jpg'.format(person_id))


class CommentedFilms(View):

    def get(self, *args, **kwargs):
        cf_html = cache.get('cf_html')
        if cf_html:
            return HttpResponse(cf_html)
        else:
            cf_html = ''
            ids = (f.id for f in Films.get_commented_films(greater=2))
            films = Films.objects.exclude(id__in=ids).order_by('-rating_sort').iterator()

            for i, f in enumerate(films):
                if i > 1000: break
                link = reverse('film_view', args=[f.id])
                year = f.release_date.year if f.release_date else ''
                cf_html += u'<a href="{}">{}</a>, {}<br>\n'.format(link, f.name, year)

            cache.set('cf_html', cf_html, 60 * 5)
            return HttpResponse(cf_html)
