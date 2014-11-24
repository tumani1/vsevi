# coding: utf-8

from __future__ import absolute_import
import os
import logging
import djcelery
from datetime import timedelta
from ConfigParser import RawConfigParser
from kombu import Exchange, Queue
from celery.schedules import crontab


###########################################################
# Celery settings
os.environ["CELERY_LOADER"] = "django"
djcelery.setup_loader()

AMQP_HOST = 'localhost'
BROKER_HOST = 'localhost'
BROKER_PORT = 5672

CELERY_ENABLE_UTC = False
CELERY_ALWAYS_EAGER = False
CELERY_CREATE_MISSING_QUEUES = True
CELERYD_PREFETCH_MULTIPLIER = 1

CELERY_TIMEZONE = 'UTC'
CELERY_ACCEPT_CONTENT = ['pickle', 'json']

CELERY_DEFAULT_QUEUE = 'default'
MAIL_QUEUE = 'mail'
NOTIFY_QUEUE = 'notify'
CAST_QUEUE = 'casts'
DATA_QUEUE = 'data'
LOCATION_QUEUE_S = 'location_singular'
LOCATION_QUEUE_P = 'location_plural'

MAIN_EXCHANGE = Exchange(name='main', type='topic', delivery_mode='persistent', durable=True)
X_DEAD_EXCHANGE = Exchange(name='wait', type='direct', delivery_mode='persistent', durable=True)

CELERY_QUEUES = (
    Queue(CELERY_DEFAULT_QUEUE, MAIN_EXCHANGE, routing_key='default'),
    Queue(MAIL_QUEUE, MAIN_EXCHANGE, routing_key='default.mail'),
    Queue(NOTIFY_QUEUE, MAIN_EXCHANGE, routing_key='default.notify'),
    Queue(CAST_QUEUE, MAIN_EXCHANGE, routing_key='default.casts'),
    Queue(DATA_QUEUE, MAIN_EXCHANGE, routing_key='default.data'),
    Queue(LOCATION_QUEUE_S, MAIN_EXCHANGE, routing_key='location.singular'),
    Queue(LOCATION_QUEUE_P, MAIN_EXCHANGE, routing_key='location.plural'),
)

###########################################################
# Base path for project
BASE_PATH = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(BASE_PATH)

STATIC_PATH = os.path.join(BASE_PATH, '..', 'static')
CONFIGS_PATH = os.path.join(BASE_PATH, '..', 'configs')
BACKUP_PATH = os.path.join(BASE_PATH, '..', '.backup')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7-dsc0--i_ej94w9as#-5p_5a)ql*9o80v1rs9krx!_-9%^b5$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = DEBUG

logger = logging.getLogger('factory')  # switch off factory boy logging
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.INFO)

ALLOWED_HOSTS = ['*']

ACCOUNT_ACTIVATION_DAYS = 2

AUTH_USER_EMAIL_UNIQUE = True

HTTP_SESSION_TOKEN_TYPE = b'X-MI-SESSION'
HTTP_USER_TOKEN_TYPE = b'X-MI-TOKEN'

STANDART_HTTP_SESSION_TOKEN_HEADER = b'HTTP_{}'.format(HTTP_SESSION_TOKEN_TYPE.replace('-', '_'))
STANDART_HTTP_USER_TOKEN_HEADER = b'HTTP_{}'.format(HTTP_USER_TOKEN_TYPE.replace('-', '_'))

DEFAULT_REST_API_RESPONSE = {}
PASSWORD_RESET_TIMEOUT_DAYS = 1

###########################################################
# Email config
emailconf = RawConfigParser()
emailconf.read(CONFIGS_PATH + '/email.ini')
EMAIL_HOST = emailconf.get('email', 'EMAIL_HOST')
EMAIL_PORT = emailconf.getint('email', 'EMAIL_PORT')
EMAIL_HOST_USER = emailconf.get('email', 'EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = emailconf.get('email', 'EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = emailconf.getboolean('email', 'EMAIL_USE_TLS')
EMAIL_BACKEND = emailconf.get('email', 'EMAIL_BACKEND')
DEFAULT_FROM_EMAIL = emailconf.get('email', 'DEFAULT_FROM_EMAIL')

###########################################################
# Application definition
INSTALLED_APPS = (
    # Admin-tools
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    # Django default apps
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django_nose',
    'treebeard',
    # Rest api
    'rest_framework',
    'rest_framework.authtoken',
    # Social oauth
    'social.apps.django_app.default',
    # Celery for django
    'djcelery',
    # Apps
    'apps.users',
    'apps.films',
    'apps.contents',
    'apps.robots',
    'apps.rss',
    'apps.git',
    'apps.casts',
    'crawler',
    'backup_system',
    'data',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'utils.middlewares.ThreadLocals',
    'utils.middlewares.ExceptionMiddleware',
    'utils.middlewares.AuthenticationMiddleware',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    # Social OAuth
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates/'),
    os.path.join(BASE_DIR, 'interface/'),
)

ROOT_URLCONF = 'videobase.urls'

WSGI_APPLICATION = 'videobase.wsgi.application'

# Database
dbconf = RawConfigParser()
dbconf.read(CONFIGS_PATH + '/db.ini')

DATABASES = {
    'default': {
        'ENGINE':   dbconf.get('database', 'DATABASE_ENGINE'),
        'HOST':     dbconf.get('database', 'DATABASE_HOST'),
        'NAME':     dbconf.get('database', 'DATABASE_NAME'),
        'USER':     dbconf.get('database', 'DATABASE_USER'),
        'PASSWORD': dbconf.get('database', 'DATABASE_PASSWORD'),
        'PORT':     dbconf.get('database', 'DATABASE_PORT')
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
        'PREFIX': 'weee:',
    }
}

# Backends for social auth
AUTHENTICATION_BACKENDS = (
    # OAuth
    'social.backends.vk.VKOAuth2',
    'social.backends.google.GoogleOAuth2',
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.twitter.TwitterOAuth',
    # Django
    'django.contrib.auth.backends.ModelBackend',
)

###########################################################
# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = False

###########################################################
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
MEDIA_ROOT = '/var/www/static/'
MEDIA_URL = '/static/'

STATIC_URL = '/production/static/'
STATIC_ROOT = '/var/www/'

SITE_ID = 1

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.users.backends.SessionTokenAuthentication',
    )
}

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

USERNAME_IS_FULL_EMAIL = True

###########################################################
# Default URL
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/tokenize'
LOGIN_ERROR_URL = '/'
HOST = 'vsevi.ru'

###########################################################
# Ключи для OAuth2 авторизации
# Vkontakte
SOCIAL_AUTH_VK_OAUTH2_KEY = '4296663'
SOCIAL_AUTH_VK_OAUTH2_SECRET = 'JAEQddzkBCm554iGXe6S'
SOCIAL_AUTH_VK_OAUTH2_SCOPE = ['email', ]
SOCIAL_AUTH_VK_PHOTO_FIELD = 'photo_max_orig'
SOCIAL_AUTH_VK_OAUTH2_EXTRA_DATA = [SOCIAL_AUTH_VK_PHOTO_FIELD, ]

# Facebook
SOCIAL_AUTH_FACEBOOK_KEY = '212532105624824'
SOCIAL_AUTH_FACEBOOK_SECRET = 'a99fcef38b7054279d73beb4ebb7b6cc'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', ]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {'locale': 'ru_RU'}

# Twitter
SOCIAL_AUTH_TWITTER_KEY = 'HACuJARrAXJyeHdeD5viHULZR'
SOCIAL_AUTH_TWITTER_SECRET = 'Ge0k2rKltyPq3ida76IjTbhesZVdIrvckcNPXzJaBU2ouzixut'

# Google+
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '729866043170.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'Ga91PMNEXi28egLsTUy5Wqhw'

SOCIAL_AUTH_GOOGLE_OAUTH2_USE_UNIQUE_USER_ID = True
SOCIAL_AUTH_GOOGLE_OAUTH2_IGNORE_DEFAULT_SCOPE = True
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

SOCIAL_AUTH_CREATE_USERS = True
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True

SOCIAL_AUTH_STORAGE = 'social.apps.django_app.default.models.DjangoStorage'

# Перечислим pipeline, которые последовательно буду обрабатывать респонс
SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'utils.pipeline.get_firstname',
    'utils.pipeline.get_email',
    'social.pipeline.user.get_username',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'utils.pipeline.load_avatar',
)

# In minutes
API_SESSION_EXPIRATION_TIME = 15
SESSION_EXPIRATION_TIME = timedelta(minutes=API_SESSION_EXPIRATION_TIME)

HAPROXY_ADDRESS = '127.0.0.1:11800'

###########################################################
DATAROBOTS_SCHEDULE = {
    # Updating information about persons using kinopoisk
    #'kinopoisk_persons': {
    #    'task': 'parse_kinopoisk_persons',
    #    'schedule': timedelta(seconds=10),
    #},
    'update_rating_command': {
        'task': 'update_ratings_task',
        'schedule': timedelta(days=3),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.data'}
    },
    'kinopoisk-set_poster': {
        'task': 'kinopoisk_set_poster',
        'schedule': timedelta(seconds=10),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.data'}
    },
    'kinopoisk_news': {
        'task': 'parse_kinopoisk_news',
        'schedule': timedelta(days=3),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.data'}
    },
    'youtube_trailers': {
        'task': 'trailer_commands',
        'schedule': timedelta(days=1),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.data'}
    },
    'kinopoisk_films_daily': {
        'task': 'kinopoisk_films',
        'schedule': timedelta(days=1),
        'args': (3,),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.data'}
    },
    'kinopoisk_films_weekly': {
        'task': 'kinopoisk_films',
        'schedule': timedelta(days=7),
        'args': (10,),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.data'}
    },
    'kinopoisk_films_monthly': {
        'task': 'kinopoisk_films',
        'schedule': timedelta(days=31),
        'args': (1100,),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.data'}
    },
    'kinopoisk_refresh': {
        'task': 'create_due_refresh_tasks',
        'schedule': timedelta(days=1),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.data'}
    },
    'film_info_check_and_correct': {
        'task': 'check_and_correct_tasks',
        'schedule': timedelta(days=7),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.data'}
    },
    'persons_check_and_correct': {
        'task': 'person_check_and_correct_tasks',
        'schedule': timedelta(days=7),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.data'}
    },

}

LOCATIONROBOTS_SCHEDULE = {
    'amediateka_ru_update': {
        'task': 'amediateka_robot_start',
        'schedule': timedelta(days=7),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'location.singular'}
    },
    'viaplay_ru_robot_start': {
        'task': 'viaplay_robot_start',
        'schedule': timedelta(days=7),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'location.singular'}
    },
    'playfamily_xml': {
        'task': 'pltask',
        'schedule': timedelta(days=7),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'location.singular'}
    },
    'drugoe_kino_update_schedule': {
        'task': 'dg_update',
        'schedule': timedelta(days=7),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'location.singular'}
    },
    'parse_you_tube_movies_ru': {
        'task': 'parse_you_tube_movies_ru',
        'schedule': timedelta(days=1),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'location.singular'}
    },
    'age_weighted_robot_launch_task_weekly': {
        'task': 'age_weighted_robot_launcher',
        'schedule': timedelta(days=3),
        'args': (1,),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'location.plural'}
    },
    'age_weighted_robot_launch_task_monthly': {
        'task': 'age_weighted_robot_launcher',
        'schedule': timedelta(days=7),
        'args': (3,),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'location.plural'}
    },
    'age_weighted_robot_launch_task_six_month': {
        'task': 'age_weighted_robot_launcher',
        'schedule': timedelta(days=14),
        'args': (120,),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'location.plural'}
    },
    'parse_news_from_now_ru': {
        'task': 'parse_news_from_now_ru',
        'schedule': timedelta(hours=12),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.location'}  #TODO
    },
    'parse_news_from_stream_ru': {
        'task': 'parse_news_from_stream_ru',
        'schedule': timedelta(hours=12),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.location'}  #TODO
    },
    'parse_news_from_tvzor_ru': {
        'task': 'parse_news_from_tvzor_ru',
        'schedule': timedelta(hours=12),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.location'}  #TODO
    },
    'itunes_update': {
        'task': 'itunes_robot_start',
        'schedule': timedelta(hours=24),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.location'}  #TODO
    },
    'mail_movies_update': {
        'task': 'mail_robot_start',
        'schedule': timedelta(hours=24),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.location'}  #TODO
    },
}

CASTROBOT_SCHEDULE = {
    'sportbox_update': {
        'task': 'sportbox_update',
        'schedule': timedelta(hours=24),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.casts'}
    },
    'liverussia_update': {
        'task': 'liverussia_update',
        'schedule': timedelta(hours=24),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.casts'}
    },
    'championat_update': {
        'task': 'championat_update',
        'schedule': timedelta(hours=24),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.casts'}
    },
    'khl_update': {
        'task': 'khl_update',
        'schedule': timedelta(hours=24),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.casts'}
    },
    'ntv_plus_update': {
        'task': 'ntv_plus_update',
        'schedule': timedelta(hours=24),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.casts'}
    }
}


CELERYBEAT_SCHEDULE = {
    'sitemap_refresh_schedule': {
        'task': 'refresh_sitemap',
        'schedule': timedelta(days=14)
    },
    'consolidate_rating_schedule': {
        'task': 'consolidate_rating',
        'schedule': timedelta(days=1)
    },
    'send_robots_statistic_to_email_schedule': {
        'task': 'send_robots_statistic_to_email',
        'schedule': timedelta(days=1),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.mail'}
    },
    'calc_amount_subscribed_to_movie': {
        'task': 'calc_amount_subscribed_to_movie',
        'schedule': timedelta(hours=1)
    },
    'week_newsletter_schedule': {
        'task': 'week_newsletter',
        'schedule': crontab(minute=0, hour=16, day_of_week=6),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.mail'}
    },
    'personal_newsletter_schedule': {
        'task': 'personal_newsletter',
        'schedule': crontab(minute=0, hour=18),
        'options': {'exchange': MAIN_EXCHANGE.name,
                    'routing_key': 'default.mail'}
    }
}
CELERYBEAT_SCHEDULE.update(DATAROBOTS_SCHEDULE)
CELERYBEAT_SCHEDULE.update(LOCATIONROBOTS_SCHEDULE)
CELERYBEAT_SCHEDULE.update(CASTROBOT_SCHEDULE)

POSTER_URL_PREFIX = '_260x360'
# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

USE_THOR = True

try:
    from .local_settings import *
except ImportError:
    pass

if not DEBUG:
    INSTALLED_APPS += (
        'raven.contrib.django.raven_compat',  # may be delete later
    )

    RAVEN_CONFIG = {
        'dsn': 'http://8684bf8b497047d9ac170fd16aefc873:41e89f4666b24f998125370f3d1a1789@sentry.aaysm.com/2'
    }

ROBOTS_LIST = ['amediateka_ru', 'ayyo_ru', 'drugoe_kino', 'itunes', 'viaplay_ru', 'youtube_com' ]
