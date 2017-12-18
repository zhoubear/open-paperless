from __future__ import absolute_import, unicode_literals

from . import *  # NOQA

# Update this accordingly;
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

TEMPLATES[0]['OPTIONS']['loaders'] = (
    (
        'django.template.loaders.cached.Loader', (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        )
    ),
)

CELERY_ALWAYS_EAGER = False
