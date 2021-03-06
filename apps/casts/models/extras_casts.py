# coding: utf-8
from django.db import models


################################################################################
# Модель Пользовательских трансляций
class CastsExtras(models.Model):
    cast  = models.ForeignKey('Casts', verbose_name=u'Идентификатор пользоваля')
    extra = models.ForeignKey('CastExtrasStorage', verbose_name=u'Extra')

    def __unicode__(self):
        return u'[{0}] {1} - {2}'.format(self.pk, self.cast.title, self.extra)

    class Meta:
        # Имя таблицы в БД
        db_table = 'extras_casts'
        app_label = 'casts'
        verbose_name = u'Трансляции extra'
        verbose_name_plural = u'Трансляции extra'
