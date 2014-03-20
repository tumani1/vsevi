# coding: utf-8

import os

from django.db import models
from django.utils.safestring import mark_safe
from ..constants import APP_PERSON_PHOTO_DIR
from utils.common import *


#############################################################################################################
# Модель Персон
class Persons(models.Model):
    name      = models.CharField(max_length=255, verbose_name=u'Имя')
    name_orig = models.CharField(max_length=255, verbose_name=u'Оригинальное имя')
    bio       = models.TextField(verbose_name=u'Биография')
    photo     = models.ImageField(upload_to=get_image_path, blank=True, null=True, verbose_name=u'Фото')


    @property
    def get_full_name(self):
        full_name = u"{0} ({1})".format(self.name, self.name_orig)
        return full_name.strip()

    @property
    def get_upload_to(self):
        return APP_PERSON_PHOTO_DIR

    def image_file(self):
        if self.photo:
            return self.get_thumbnail_html()
        else:
            return '(none)'

    @property
    def get_thumbnail_html(self):
        html = '<a class="image-picker" href="%s"><img src="%s" alt="%s"/></a>'
        return html % (self.photo.url, get_thumbnail_url(self.photo.url), "")

    image_file.short_description = 'thumbnail'
    image_file.allow_tags = True

    def save(self, *args, **kwargs):
        is_new = self.pk == None
        super(Persons, self).save(*args, **kwargs)

        if is_new:
            instance_photo = self.photo
            if instance_photo:
                # Create new filename, using primary key
                oldfile = self.photo.name
                newfile = os.path.join(APP_PERSON_PHOTO_DIR, str(self.id), oldfile.split("/")[-1])

                # Magic with photo
                self.photo.storage.delete(newfile)
                self.photo.storage.save(newfile, instance_photo)
                self.photo.name = newfile
                self.photo.close()
                self.photo.storage.delete(oldfile)

                # Save again to keep changes
                super(Persons, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'[%s] %s' % (self.pk, self.get_full_name)

    class Meta:
        # Имя таблицы в БД
        db_table = 'persons'
        app_label = 'Films'
        verbose_name = u'Персона'
        verbose_name_plural = u'Персоны'
