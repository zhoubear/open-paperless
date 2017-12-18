from __future__ import unicode_literals

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from common import MayanAppConfig, menu_tools
from navigation import SourceColumn
from rest_api.classes import APIEndPoint

from .links import link_events_list
from .licenses import *  # NOQA
from .widgets import event_object_link, event_type_link


def event_actor(action):
    return _('System') if action.actor == action.target else action.actor


def event_action_object(action):
    return action.action_object if action.action_object != action.target and action.action_object else ''


class EventsApp(MayanAppConfig):
    has_tests = True
    name = 'events'
    verbose_name = _('Events')

    def ready(self):
        super(EventsApp, self).ready()
        Action = apps.get_model(app_label='actstream', model_name='Action')

        APIEndPoint(app=self, version_string='1')

        SourceColumn(
            source=Action, label=_('Timestamp'), attribute='timestamp'
        )
        SourceColumn(
            source=Action, label=_('Actor'),
            func=lambda context: event_actor(context['object'])
        )
        SourceColumn(
            source=Action, label=_('Verb'),
            func=lambda context: event_type_link(context['object'])
        )
        SourceColumn(
            source=Action, label=_('Action object'),
            func=lambda context: event_object_link(
                entry=context['object'], attribute='action_object'
            )
        )

        menu_tools.bind_links(links=(link_events_list,))
