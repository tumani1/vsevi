# coding: utf-8

import json

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.tasks import film_notification
from apps.users.models import User, UsersProfile, Feed
from apps.users.constants import FILM_O, PERSON_O

from rest_framework.authtoken.models import Token


@receiver(post_save, sender=get_user_model())
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=User)
def add_profile_to_user(instance, **kwargs):
    profile, flag = UsersProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=Feed)
def add_feed(instance, created, **kwargs):
    if created:
        if instance.type in (PERSON_O, FILM_O,):
            kw = {
                'id_': instance.obj_id,
                'type_': instance.type,
                'child_obj': instance.child_obj_id
            }

            film_notification.apply_async(kwargs=kw)
