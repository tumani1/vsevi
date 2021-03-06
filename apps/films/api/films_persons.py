# coding: utf-8

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.films.models import PersonsFilms, Persons
from apps.films.forms import PersonApiForm
from apps.films.api.serializers import vbPerson
from apps.films.constants import APP_FILM_PERSON_TYPES_OUR

from videobase.settings import DEFAULT_REST_API_RESPONSE

#############################################################################################################
class PersonsFilmView(APIView):
    """
    Returns all persons by film
    """

    def __get_object(self, film_id, cleaned_data):
        """
        Return object Films or Response object with 404 error
        """

        filter = {
            'film': film_id,
        }

        if cleaned_data['type'] and cleaned_data['type'] != 'all':
            filter.update({'p_type': dict(APP_FILM_PERSON_TYPES_OUR)[cleaned_data['type']]})

        result = PersonsFilms.objects.filter(**filter).\
                     values_list('person', flat=True)

        if not len(result):
            return Response(DEFAULT_REST_API_RESPONSE, status=status.HTTP_404_NOT_FOUND)

        return result


    def get(self, request, film_id, format=None, *args, **kwargs):
        self.get_copy = request.GET.copy()
        form = PersonApiForm(data=self.get_copy)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            person_list = self.__get_object(film_id, cleaned_data)
            if type(person_list) == Response:
                return person_list

            filter = {
                'filter': {'pk__in': person_list},
                'offset': cleaned_data['top'],
            }

            if cleaned_data['limit']:
                filter.update({'limit': cleaned_data['limit'] + cleaned_data['top']})

            o_person = Persons.get_sorted_persons_by_name(**filter)
            serializer = vbPerson(o_person, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
