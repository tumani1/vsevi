# coding: utf-8

from django.db import models

from apps.films.models import Films, Seasons


#############################################################################################################
# Модель Контента
class Contents(models.Model):
    film                 = models.ForeignKey(Films, verbose_name=u'Фильм')
    name                 = models.CharField(max_length=255, verbose_name=u'Название')
    name_orig            = models.CharField(max_length=255, verbose_name=u'Оригинальное название')
    number               = models.IntegerField(null=True, blank=True, verbose_name=u'Номер сезона')
    description          = models.TextField(verbose_name=u'Описание')
    release_date         = models.DateTimeField(verbose_name=u'Дата выхода')
    season               = models.ForeignKey(Seasons, null=True, blank=True, verbose_name=u'Сезоны')
    viewer_cnt           = models.IntegerField(verbose_name=u'Количество посмотревших за все время')
    viewer_lastweek_cnt  = models.IntegerField(verbose_name=u'Количество посмотревших за последнюю неделю')
    viewer_lastmonth_cnt = models.IntegerField(verbose_name=u'Количество посмотревших за последний месяц')


    def __unicode__(self):
        return u'[{:s}] {:s}'.format(self.pk, self.film.name,)

    class Meta:
        # Имя таблицы в БД
        db_table = 'content'
        app_label = 'Contents'
        verbose_name = u'Контент'
        verbose_name_plural = u'Контент'