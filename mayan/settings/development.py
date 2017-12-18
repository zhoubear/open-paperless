from __future__ import absolute_import, unicode_literals

from . import *  # NOQA

DEBUG = True

ALLOWED_HOSTS = ['*']

TEMPLATES[0]['OPTIONS']['loaders'] = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

INSTALLED_APPS += (
    'rosetta',
    'django_extensions',
)

WSGI_AUTO_RELOAD = True

CELERY_EAGER_PROPAGATES_EXCEPTIONS = CELERY_ALWAYS_EAGER
