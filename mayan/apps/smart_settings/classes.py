from __future__ import unicode_literals

from importlib import import_module
import logging
import os

import yaml

from django.apps import apps
from django.conf import settings
from django.utils.functional import Promise
from django.utils.encoding import force_text, python_2_unicode_compatible

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Namespace(object):
    _registry = {}

    @staticmethod
    def initialize():
        for app in apps.get_app_configs():
            try:
                import_module('{}.settings'.format(app.name))
            except ImportError as exception:
                if force_text(exception) not in ('No module named settings', 'No module named \'{}.settings\''.format(app.name)):
                    logger.error(
                        'Error importing %s settings.py file; %s', app.name,
                        exception
                    )

    @classmethod
    def get_all(cls):
        return sorted(cls._registry.values(), key=lambda x: x.label)

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    @classmethod
    def invalidate_cache_all(cls):
        for namespace in cls.get_all():
            namespace.invalidate_cache()

    def __str__(self):
        return force_text(self.label)

    def __init__(self, name, label):
        if name in self.__class__._registry:
            raise Exception(
                'Namespace names must be unique; "%s" already exists.' % name
            )
        self.name = name
        self.label = label
        self.__class__._registry[name] = self
        self._settings = []

    def add_setting(self, **kwargs):
        return Setting(namespace=self, **kwargs)

    def invalidate_cache(self):
        for setting in self._settings:
            setting.invalidate_cache()

    @property
    def settings(self):
        return sorted(self._settings, key=lambda x: x.global_name)


@python_2_unicode_compatible
class Setting(object):
    _registry = {}

    @staticmethod
    def deserialize_value(value):
        return yaml.safe_load(value)

    @staticmethod
    def serialize_value(value):
        if isinstance(value, Promise):
            value = force_text(value)

        result = yaml.safe_dump(value, allow_unicode=True)
        # safe_dump returns bytestrings
        # Disregard the last 3 dots that mark the end of the YAML document
        if force_text(result).endswith('...\n'):
            result = result[:-4]

        return result

    @classmethod
    def get(cls, global_name):
        return cls._registry[global_name].value

    def __init__(self, namespace, global_name, default, help_text=None, is_path=False):
        self.global_name = global_name
        self.default = default
        self.help_text = help_text
        self.loaded = False
        namespace._settings.append(self)
        self.__class__._registry[global_name] = self

    def __str__(self):
        return force_text(self.global_name)

    def cache_value(self):
        environment_value = os.environ.get('MAYAN_{}'.format(self.global_name))
        if environment_value:
            self.raw_value = yaml.safe_load(environment_value)
        else:
            self.raw_value = getattr(settings, self.global_name, self.default)
        self.yaml = Setting.serialize_value(self.raw_value)
        self.loaded = True

    def invalidate_cache(self):
        self.loaded = False

    @property
    def serialized_value(self):
        """
        YAML serialize value of the setting.
        Used for UI display.
        """
        if not self.loaded:
            self.cache_value()

        return self.yaml

    @property
    def value(self):
        if not self.loaded:
            self.cache_value()

        return self.raw_value

    @value.setter
    def value(self, value):
        # value is in YAML format
        self.yaml = value
        self.raw_value = Setting.deserialize_value(value)
