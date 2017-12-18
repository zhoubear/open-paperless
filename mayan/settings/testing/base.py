from __future__ import absolute_import, unicode_literals

from .. import *  # NOQA

INSTALLED_APPS += ('test_without_migrations',)
TEMPLATES[0]['OPTIONS']['loaders'] = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
