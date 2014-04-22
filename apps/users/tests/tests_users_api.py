# coding: utf-8
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from apps.users.models import User
from apps.users.models.api_session import SessionToken, UsersApiSessions
from apps.users.tests.factories import UserFactory, UserProfileFactory


class APIUsersTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.user_with_avatart = UserFactory.create()
        self.profile = UserProfileFactory.create(user=self.user)
        self.url_name = 'users'
        self.kwargs = {'format': 'json', 'user_id': self.user.pk}
        s_token = SessionToken.objects.create(user=self.user)
        UsersApiSessions.objects.create(token=s_token)
        self.headers = "%s %s" % ('X-VB-Token', s_token.key)

    def test_api_user_401_get(self):
        response = self.client.get(reverse(self.url_name, kwargs=self.kwargs))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_users_400_get(self):
        pk = User.objects.latest('id')
        self.kwargs['user_id'] = pk + 1
        response = self.client.get(reverse(self.url_name, kwargs=self.kwargs),
                                   HTTP_AUTHORIZATION=self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_users_200_get(self):
        response = self.client.get(reverse(self.url_name, kwargs=self.kwargs),
                                   HTTP_AUTHORIZATION=self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('username', None))
        self.assertIsNotNone(response.data.get('avatar', None))
        self.assertIsNotNone(response.data.get('id', None))
        self.assertEqual(response.data['id'], self.user.pk)
        self.assertEqual(response.data['username'], self.profile.nickname)
        # self.assertEqual(response.data['avatar'], self.profile.nickname)

    def test_api_user_401_post(self):
        response = self.client.post(reverse(self.url_name, kwargs=self.kwargs))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_users_400_post(self):
        pk = User.objects.latest('id')
        self.kwargs['user_id'] = pk + 1
        response = self.client.post(reverse(self.url_name, kwargs=self.kwargs),
                                   HTTP_AUTHORIZATION=self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
