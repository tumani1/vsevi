# coding: utf-8

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.films.models import PersonsFilms, Persons
from apps.films.forms import PersonApiForm
from apps.films.api.serializers import vbPerson


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

        if not cleaned_data['type'] is None:
            filter.update({'p_type': cleaned_data['type']})

        result = PersonsFilms.objects.filter(**filter).\
                     values_list('person', flat=True)[cleaned_data['top']:cleaned_data['limit']]

        if not len(result):
            return Response(status=status.HTTP_404_NOT_FOUND)

        return result


    def get(self, request, film_id, format=None, *args, **kwargs):
        self.get_copy = request.GET.copy()
        form = PersonApiForm(data=self.get_copy)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            person_list = self.__get_object(film_id, cleaned_data)
            if type(person_list) == Response:
                return person_list

            o_person = Persons.objects.filter(pk__in=person_list)

            serializer = vbPerson(o_person, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
