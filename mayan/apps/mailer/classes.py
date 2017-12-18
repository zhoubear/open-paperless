from __future__ import unicode_literals

from importlib import import_module
import logging

from django.apps import apps
from django.utils import six
from django.utils.encoding import force_text

logger = logging.getLogger(__name__)


__all__ = ('MailerBackend',)


class MailerBackendMetaclass(type):
    _registry = {}

    def __new__(mcs, name, bases, attrs):
        new_class = super(MailerBackendMetaclass, mcs).__new__(
            mcs, name, bases, attrs
        )
        if not new_class.__module__ == 'mailer.classes':
            mcs._registry[
                '{}.{}'.format(new_class.__module__, name)
            ] = new_class

        return new_class


class MailerBackendBase(object):
    """
    Base class for the mailing backends. This class is mainly a wrapper
    for other Django backends that adds a few metadata to specify the
    fields it needs to be instanciated at runtime.

    The fields attribute is a list of dictionaries with the format:
    {
        'name': ''  # Field internal name
        'label': ''  # Label to show to users
        'class': ''  # Field class to use. Field classes are Python dot
                       paths to Django's form fields.
        'initial': ''  # Field initial value
        'default': ''  # Default value.
    }

    """
    class_path = ''  # Dot path to the actual class that will handle the mail
    fields = {}


class MailerBackend(six.with_metaclass(MailerBackendMetaclass, MailerBackendBase)):
    @classmethod
    def get(cls, name):
        return cls._registry[name]

    @classmethod
    def get_all(cls):
        return cls._registry

    @staticmethod
    def initialize():
        for app in apps.get_app_configs():
            try:
                import_module('{}.mailers'.format(app.name))
            except ImportError as exception:
                if force_text(exception) not in ('No module named mailers', 'No module named \'{}.mailers\''.format(app.name)):
                    logger.error(
                        'Error importing %s mailers.py file; %s', app.name,
                        exception
                    )
