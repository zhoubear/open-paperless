from __future__ import unicode_literals

from django.conf.urls import include, url
from django.conf import settings
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.module_loading import import_string


@python_2_unicode_compatible
class APIEndPoint(object):
    _registry = {}

    @classmethod
    def get_all(cls):
        return cls._registry.values()

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    def __str__(self):
        return force_text(self.app.name)

    def __init__(self, app, version_string, name=None):
        self.app = app
        self.endpoints = []
        self.name = name
        self.version_string = version_string
        try:
            api_urls = import_string(
                '{0}.urls.api_urls'.format(app.name)
            )
        except Exception:
            if settings.DEBUG:
                raise
            else:
                # Ignore import time errors
                pass
        else:
            self.register_urls(api_urls)

        self.__class__._registry[app.name] = self

    @property
    def app_name(self):
        return self.app.name

    def register_urls(self, urlpatterns):
        from .urls import urlpatterns as app_urls

        app_urls += [
            url(r'^%s/' % (self.name or self.app.name), include(urlpatterns)),
        ]
