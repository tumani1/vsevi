# coding: utf-8
from django.db import models

from apps.films.models import Films
from ..constants import APP_ROBOTS_PARSE_TRY_RESULT_TYPES


#############################################################################################################
# Модель Кинопоиска
class KinopoiskTries(models.Model):
    film     = models.ForeignKey(Films, verbose_name=u'Фильм')
    try_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=u'Дата попытки')
    result   = models.CharField(max_length=255, choices=APP_ROBOTS_PARSE_TRY_RESULT_TYPES, verbose_name=u'Удался ли парсинг')
    error_message = models.TextField(verbose_name=u'Сообщение об ошибке', null=True)
    page_dump = models.TextField(verbose_name=u'Скачанная страница', null=True)

    @property
    def format_try_time(self):
        return self.try_time.strftime("%Y-%b-%d %H:%M:%S")

    def __unicode__(self):
        return u'[{}] {}  {}'.format(self.pk, self.film, self.format_try_time)

    class Meta:
        # Имя таблицы в БД
        db_table = 'robots_kinopoisk_tries'
        app_label = 'robots'
        verbose_name = u'Попытка кинопоиска'
        verbose_name_plural = u'Попытки кинопоиска'

