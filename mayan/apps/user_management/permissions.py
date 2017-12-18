from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('user_management', _('User management'))

permission_group_create = namespace.add_permission(
    name='group_create', label=_('Create new groups')
)
permission_group_delete = namespace.add_permission(
    name='group_delete', label=_('Delete existing groups')
)
permission_group_edit = namespace.add_permission(
    name='group_edit', label=_('Edit existing groups')
)
permission_group_view = namespace.add_permission(
    name='group_view', label=_('View existing groups')
)
permission_user_create = namespace.add_permission(
    name='user_create', label=_('Create new users')
)
permission_user_delete = namespace.add_permission(
    name='user_delete', label=_('Delete existing users')
)
permission_user_edit = namespace.add_permission(
    name='user_edit', label=_('Edit existing users')
)
permission_user_view = namespace.add_permission(
    name='user_view', label=_('View existing users')
)
