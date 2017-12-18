from __future__ import absolute_import, unicode_literals

import logging

from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from common.views import (
    SingleObjectCreateView, SingleObjectDeleteView, SingleObjectEditView,
    SingleObjectListView
)

from .models import Message
from .permissions import (
    permission_message_create, permission_message_delete,
    permission_message_edit, permission_message_view
)

logger = logging.getLogger(__name__)


class MessageCreateView(SingleObjectCreateView):
    fields = ('label', 'message', 'enabled', 'start_datetime', 'end_datetime')
    model = Message
    view_permission = permission_message_create

    def get_extra_context(self):
        return {
            'title': _('Create message'),
        }


class MessageDeleteView(SingleObjectDeleteView):
    model = Message
    object_permission = permission_message_delete
    post_action_redirect = reverse_lazy('motd:message_list')

    def get_extra_context(self):
        return {
            'message': None,
            'object': self.get_object(),
            'title': _('Delete the message: %s?') % self.get_object(),
        }


class MessageEditView(SingleObjectEditView):
    fields = ('label', 'message', 'enabled', 'start_datetime', 'end_datetime')
    model = Message
    object_permission = permission_message_edit
    post_action_redirect = reverse_lazy('motd:message_list')

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Edit message: %s') % self.get_object(),
        }


class MessageListView(SingleObjectListView):
    model = Message
    object_permission = permission_message_view

    def get_extra_context(self):
        return {
            'hide_link': True,
            'title': _('Messages'),
        }
