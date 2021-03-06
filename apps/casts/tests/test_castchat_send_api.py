# coding: utf-8
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APISimpleTestCase
from rest_framework.authtoken.models import Token

from apps.casts.models import CastsChatsMsgs, CastsChats
from apps.casts.tests.factories import UserFactory, CastsFactory, CastsChatFactory

from apps.users.models import SessionToken


class CastChatMsgSendTestCase(APISimpleTestCase):

    def setUp(self):
        self.user = UserFactory.create()
        self.cast = CastsFactory.create(tags=[])

        self.cast_chat = CastsChatFactory._get_or_create(CastsChats, cast=self.cast, status=1)

        token = Token.objects.get(user=self.user)
        s_token = SessionToken.objects.create(user=self.user)
        self.headers = s_token.key

    def test_send(self):
        COMM_TEXT = 'Commentary text'
        response = self.client.post(
            reverse('casts_api:castchat_send_view', kwargs={'cast_id': self.cast_chat.id, 'format': 'json'}),
            HTTP_X_MI_SESSION=self.headers, data={'text': COMM_TEXT}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ccm = CastsChatsMsgs.objects.filter(cast__id=self.cast_chat.cast.id, user=self.user)
        self.assertEqual(ccm[0].text, COMM_TEXT)
