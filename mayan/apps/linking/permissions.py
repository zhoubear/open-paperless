from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('linking', _('Smart links'))

permission_smart_link_view = namespace.add_permission(
    name='smart_link_view', label=_('View existing smart links')
)
permission_smart_link_create = namespace.add_permission(
    name='smart_link_create', label=_('Create new smart links')
)
permission_smart_link_delete = namespace.add_permission(
    name='smart_link_delete', label=_('Delete smart links')
)
permission_smart_link_edit = namespace.add_permission(
    name='smart_link_edit', label=_('Edit smart links')
)
