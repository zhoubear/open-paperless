from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Link

from .permissions import (
    permission_group_create, permission_group_delete, permission_group_edit,
    permission_group_view, permission_user_create, permission_user_delete,
    permission_user_edit, permission_user_view
)

link_group_add = Link(
    permissions=(permission_group_create,), text=_('Create new group'),
    view='user_management:group_add'
)
link_group_delete = Link(
    permissions=(permission_group_delete,), tags='dangerous', text=_('Delete'),
    view='user_management:group_delete', args='object.id'
)
link_group_edit = Link(
    permissions=(permission_group_edit,), text=_('Edit'),
    view='user_management:group_edit', args='object.id'
)
link_group_list = Link(
    permissions=(permission_group_view,), text=_('Groups'),
    view='user_management:group_list'
)
link_group_members = Link(
    permissions=(permission_group_edit,), text=_('Members'),
    view='user_management:group_members', args='object.id'
)
link_group_setup = Link(
    icon='fa fa-group', permissions=(permission_group_view,), text=_('Groups'),
    view='user_management:group_list'
)
link_user_add = Link(
    permissions=(permission_user_create,), text=_('Create new user'),
    view='user_management:user_add'
)
link_user_delete = Link(
    permissions=(permission_user_delete,), tags='dangerous', text=_('Delete'),
    view='user_management:user_delete', args='object.id'
)
link_user_edit = Link(
    permissions=(permission_user_edit,), text=_('Edit'),
    view='user_management:user_edit', args='object.id'
)
link_user_groups = Link(
    permissions=(permission_user_edit,), text=_('Groups'),
    view='user_management:user_groups', args='object.id'
)
link_user_list = Link(
    permissions=(permission_user_view,), text=_('Users'),
    view='user_management:user_list'
)
link_user_multiple_delete = Link(
    permissions=(permission_user_delete,), tags='dangerous', text=_('Delete'),
    view='user_management:user_multiple_delete'
)
link_user_multiple_set_password = Link(
    permissions=(permission_user_edit,), text=_('Set password'),
    view='user_management:user_multiple_set_password'
)
link_user_set_password = Link(
    permissions=(permission_user_edit,), text=_('Set password'),
    view='user_management:user_set_password', args='object.id'
)
link_user_setup = Link(
    icon='fa fa-user', permissions=(permission_user_view,), text=_('Users'),
    view='user_management:user_list'
)
