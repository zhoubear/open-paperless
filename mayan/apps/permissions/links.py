from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Link

from .permissions import (
    permission_permission_grant, permission_permission_revoke,
    permission_role_create, permission_role_delete, permission_role_edit,
    permission_role_view
)

link_permission_grant = Link(
    permissions=(permission_permission_grant,), text=_('Grant'),
    view='permissions:permission_multiple_grant'
)
link_permission_revoke = Link(
    permissions=(permission_permission_revoke,), text=_('Revoke'),
    view='permissions:permission_multiple_revoke'
)
link_role_create = Link(
    permissions=(permission_role_create,), text=_('Create new role'),
    view='permissions:role_create'
)
link_role_delete = Link(
    permissions=(permission_role_delete,), tags='dangerous', text=_('Delete'),
    view='permissions:role_delete', args='object.id'
)
link_role_edit = Link(
    permissions=(permission_role_edit,), text=_('Edit'),
    view='permissions:role_edit', args='object.id'
)
link_role_list = Link(
    icon='fa fa-user-secret', permissions=(permission_role_view,),
    text=_('Roles'), view='permissions:role_list'
)
link_role_members = Link(
    permissions=(permission_role_edit,), text=_('Members'),
    view='permissions:role_members', args='object.id'
)
link_role_permissions = Link(
    permissions=(permission_permission_grant, permission_permission_revoke),
    text=_('Role permissions'), view='permissions:role_permissions',
    args='object.id'
)
