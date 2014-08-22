# coding: utf-8

from django.db import models

#############################################################################################################
# Модель Тегов Трансляций
class AbstractCastsTags(models.Model):

    name   = models.CharField(max_length=255, default='', blank=True, db_index=True, verbose_name=u'Оригинальное название тега')
    name_orig   = models.CharField(max_length=255, default='', blank=True, db_index=True, verbose_name=u'Оригинальное название тега')
    description = models.TextField(max_length=255, db_index=True, blank=False, verbose_name=u'Описание')
    type   = models.CharField(max_length=255, default='', blank=True, db_index=True, verbose_name=u'Тип')
        

    def __unicode__(self):
        return u'[{0}] {1}'.format(self.pk, self.name)

        
    class  Meta(object):
        # Имя таблицы в БД
        db_table = 'abstract_casts_tags'
        app_label = 'casts'
        verbose_name = u'Тег трансляции'
        verbose_name_plural = u'Теги трансляции'
        