# coding: utf-8

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

from ..constants import *


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
           raise ValueError('Users must have an email address')
        user = self.model(email=UserManager.normalize_email(email), **kwargs)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        user = self.model(email=UserManager.normalize_email(email), is_admin=True, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user


#############################################################################################################
# Модель Пользователей
class Users(AbstractBaseUser):
    auth         = models.ForeignKey(User, verbose_name=u'')
    firstname    = models.CharField(max_length=255, verbose_name=u'Имя')
    lastname     = models.CharField(max_length=255, verbose_name=u'Фамилия')
    email        = models.EmailField(max_length=255, unique=True, verbose_name=u'Email')
    last_visited = models.DateTimeField(auto_now_add=True, verbose_name=u'Последний визит')
    created      = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=u'Дата создания')
    ustatus      = models.PositiveSmallIntegerField(choices=APP_USER_STATUS, default=APP_USER_ACTIVE, verbose_name=u'Статус')
    userpic_type = models.CharField(null=True, blank=True, default=None, choices=APP_USER_PIC_TYPES, max_length=255, verbose_name=u'Тип картинки')
    userpic      = models.ForeignKey('UsersPics', default=None, null=True, blank=True, verbose_name=u'Аватар', related_name='+')
    is_admin     = models.BooleanField(default=False, null=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __unicode__(self):
        return u'[%s] %s' % (self.pk, self.name)

    @property
    def name(self):
        """
        Get full name through a divider
        """
        full_name = u'%s %s' % (self.firstname, self.lastname)
        return full_name.strip()

    get_full_name = name
    get_short_name = name

    def is_superuser(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    class Meta:
        # Имя таблицы в БД
        db_table = 'users'
        app_label = 'users'
        verbose_name = u'Пользователь'
        verbose_name_plural = u'Пользователи'
