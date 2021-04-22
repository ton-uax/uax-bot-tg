import os

from core.env import ROOT, env
from celery.schedules import crontab
from django.utils import timezone

SECRET_KEY = env.str('CORE_SECRET_KEY', default='secret')

DEBUG = env.bool('CORE_DEBUG', default=True)

ALLOWED_HOSTS = env.list("CORE_ALLOWED_HOSTS", default=["*"])


# Application definition
INSTALLED_APPS = [
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'django_celery_results',

    # 3rd party apps
    "rest_framework",

    # Project apps
    'core.apps.common',
    'core.apps.account',
    'core.apps.wallet',
    'core.apps.broadcast',

]

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar', 'django_extensions', ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

ROOT_URLCONF = 'core.config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(ROOT, "templates")],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'admin_tools.template_loaders.Loader',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.config.wsgi.application'

DATABASES = {
    'default': env.db('CORE_DATABASE_URL', default='psql:///clubhouse_db'),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-ru'
gettext = lambda s: s

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

PROJECT_ROOT = ROOT - 2
DEFAULT_PUBLIC_ROOT = os.path.join(PROJECT_ROOT, "public/static")

STATIC_URL = env.str("CORE_STATIC_URL", default="/static/")
MEDIA_URL = env.str("CORE_MEDIA_URL", default="/media/")

# production usage
STATIC_ROOT = env.str("CORE_STATIC_ROOT", DEFAULT_PUBLIC_ROOT)

# development usage
STATICFILES_DIRS = (
    ROOT("static"),
)

CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_BEAT_SCHEDULE = {

    # "broadcast": {
    #     "task": "core.apps.broadcast.tasks.check_broadcast_query",
    #     "schedule": crontab(minute='*/2')
    # },
    "check_balance": {
        "task": "core.apps.wallet.tasks.check_balance",
        "schedule": 5
    },
    "check_fee": {
        "task": "core.apps.wallet.tasks.check_fee",
        "schedule": 30
    },

}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

ADMIN_TOOLS_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'
#ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'dashboard.CustomAppIndexDashboard'
ADMIN_TOOLS_MENU = 'menu.CustomMenu'
