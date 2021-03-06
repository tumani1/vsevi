# coding: utf-8
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APISimpleTestCase
from rest_framework.authtoken.models import Token

from apps.casts.models import UsersCasts, CastsChats
from apps.casts.tests.factories import UserFactory, CastsFactory, CastsChatFactory

from apps.users.models import SessionToken


class RatingTestCase(APISimpleTestCase):

    def setUp(self):
        self.user = UserFactory.create()
        self.cast = CastsFactory.create(tags=[])

        self.cast_chat = CastsChatFactory._get_or_create(CastsChats, cast=self.cast, status=1)

        token = Token.objects.get(user=self.user)
        s_token = SessionToken.objects.create(user=self.user)
        self.headers = s_token.key

    def test_rating(self):
        response = self.client.post(
            reverse('casts_api:cast_rating_view', kwargs={'cast_id': self.cast_chat.id, 'format': 'json'}),
            HTTP_X_MI_SESSION=self.headers, data={'rating': 5}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        uc = UsersCasts.objects.filter(cast__id=self.cast.id, user=self.user)
        self.assertEqual(uc[0].rating, 5)
