from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('acls', _('Access control lists'))

permission_acl_edit = namespace.add_permission(
    name='acl_edit', label=_('Edit ACLs')
)
permission_acl_view = namespace.add_permission(
    name='acl_view', label=_('View ACLs')
)
