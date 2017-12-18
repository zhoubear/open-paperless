from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('motd', _('Message of the day'))

permission_message_create = namespace.add_permission(
    name='message_create', label=_('Create messages')
)
permission_message_delete = namespace.add_permission(
    name='message_delete', label=_('Delete messages')
)
permission_message_edit = namespace.add_permission(
    name='message_edit', label=_('Edit messages')
)
permission_message_view = namespace.add_permission(
    name='message_view', label=_('View messages')
)
