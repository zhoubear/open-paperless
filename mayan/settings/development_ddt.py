from __future__ import absolute_import, unicode_literals

from .development import *  # NOQA

INSTALLED_APPS += (
    'debug_toolbar',
)

# Stop debug toolbar patching!
# see https://github.com/django-debug-toolbar/django-debug-toolbar/issues/524
DEBUG_TOOLBAR_PATCH_SETTINGS = False

WSGI_AUTO_RELOAD = True

MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES
