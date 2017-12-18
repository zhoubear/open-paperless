from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Link

from .permissions import (
    permission_message_create, permission_message_delete,
    permission_message_edit,
)

link_message_create = Link(
    permissions=(permission_message_create,), text=_('Create message'),
    view='motd:message_create'
)
link_message_delete = Link(
    permissions=(permission_message_delete,), tags='dangerous',
    text=_('Delete'), view='motd:message_delete', args='object.pk'
)
link_message_edit = Link(
    permissions=(permission_message_edit,), text=_('Edit'),
    view='motd:message_edit', args='object.pk'
)
link_message_list = Link(
    icon='fa fa-bullhorn', text=_('Message of the day'),
    view='motd:message_list'
)
