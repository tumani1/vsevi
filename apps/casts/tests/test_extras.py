#coding: utf-8
from rest_framework.test import APISimpleTestCase
from apps.casts.tests.factories import TagFactory, CastsFactory, CastsExtrasFactory
from rest_framework.reverse import reverse
from rest_framework import status

class CastTestCase(APISimpleTestCase):

    def setUp(self):

        self.tags = [TagFactory.create()]
        self.cast_extras = CastsExtrasFactory.create()


    def test_search(self):

        response = self.client.get(reverse('cast_extras_view',
                                kwargs={'cast_id':1, 'format':'json'}
                            ), data = {})

        self.assertEqual(response.status_code , status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], 1)


