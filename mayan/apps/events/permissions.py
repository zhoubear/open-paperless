from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('events', _('Events'))
permission_events_view = namespace.add_permission(
    name='events_view', label=_('Access the events of an object')
)
