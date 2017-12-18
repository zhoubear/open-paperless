from __future__ import unicode_literals

from .base import *  # NOQA

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'xe',
        'USER': 'system',
        'HOST': '127.0.0.1',
        'PORT': '49161',
        'PASSWORD': 'oracle',
    }
}
