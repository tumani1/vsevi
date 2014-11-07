# coding: utf-8

from django.apps import AppConfig


class FilmConfig(AppConfig):
    name = 'apps.films'

    def ready(self):

        # import signal
        import apps.films.signals
