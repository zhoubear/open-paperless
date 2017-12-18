from __future__ import unicode_literals

from django.apps import apps
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from actstream import action


class Event(object):
    _registry = {}

    @classmethod
    def all(cls):
        return Event.sort(event_type_list=cls._registry.values())

    @classmethod
    def get(cls, name):
        try:
            return cls._registry[name]
        except KeyError:
            raise KeyError(
                _('Unknown or obsolete event type: {0}'.format(name))
            )

    @classmethod
    def get_label(cls, name):
        try:
            return cls.get(name=name).label
        except KeyError as exception:
            return force_text(exception)

    @classmethod
    def refresh(cls):
        for event_type in cls.all():
            event_type.get_type()

    @staticmethod
    def sort(event_type_list):
        return sorted(
            event_type_list, key=lambda x: x.label
        )

    def __init__(self, name, label):
        self.name = name
        self.label = label
        self.event_type = None
        self.__class__._registry[name] = self

    def get_type(self):
        if not self.event_type:
            EventType = apps.get_model('events', 'EventType')

            self.event_type, created = EventType.objects.get_or_create(
                name=self.name
            )

        return self.event_type

    def commit(self, actor=None, action_object=None, target=None):
        if not self.event_type:
            EventType = apps.get_model('events', 'EventType')
            self.event_type, created = EventType.objects.get_or_create(
                name=self.name
            )

        action.send(
            actor or target, actor=actor, verb=self.name,
            action_object=action_object, target=target
        )
