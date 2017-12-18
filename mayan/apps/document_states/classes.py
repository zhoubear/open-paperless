from __future__ import unicode_literals

from importlib import import_module
import logging

from django.apps import apps
from django.utils import six
from django.utils.encoding import force_text

from common.classes import PropertyHelper

__all__ = ('WorkflowAction',)
logger = logging.getLogger(__name__)


class DocumentStateHelper(PropertyHelper):
    @staticmethod
    @property
    def constructor(*args, **kwargs):
        return DocumentStateHelper(*args, **kwargs)

    def get_result(self, name):
        return self.instance.workflows.get(workflow__internal_name=name)


class WorkflowActionMetaclass(type):
    _registry = {}

    def __new__(mcs, name, bases, attrs):
        new_class = super(WorkflowActionMetaclass, mcs).__new__(
            mcs, name, bases, attrs
        )

        if not new_class.__module__ == __name__:
            mcs._registry[
                '{}.{}'.format(new_class.__module__, name)
            ] = new_class

        return new_class


class WorkflowActionBase(object):
    fields = ()


class WorkflowAction(six.with_metaclass(WorkflowActionMetaclass, WorkflowActionBase)):
    @classmethod
    def clean(cls, request, form_data=None):
        return form_data

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    @classmethod
    def get_all(cls):
        return sorted(cls._registry.values(), key=lambda x: x.label)

    @classmethod
    def id(cls):
        return '{}.{}'.format(cls.__module__, cls.__name__)

    @staticmethod
    def initialize():
        for app in apps.get_app_configs():
            try:
                import_module('{}.workflow_actions'.format(app.name))
            except ImportError as exception:
                if force_text(exception) not in ('No module named workflow_actions', 'No module named \'{}.workflow_actions\''.format(app.name)):
                    logger.error(
                        'Error importing %s workflow_actions.py file; %s',
                        app.name, exception
                    )

    def __init__(self, form_data=None):
        self.form_data = form_data

    def get_form_schema(self, request=None):
        result = {
            'fields': self.fields or (),
            'widgets': getattr(self, 'widgets', {})
        }

        if hasattr(self, 'field_order'):
            result['field_order'] = self.field_order

        return result
