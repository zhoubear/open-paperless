from __future__ import unicode_literals

from .base import *  # NOQA

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mayan_edms',
        'USER': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
