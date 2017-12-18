from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('comments', _('Comments'))

permission_comment_create = namespace.add_permission(
    name='comment_create', label=_('Create new comments')
)
permission_comment_delete = namespace.add_permission(
    name='comment_delete', label=_('Delete comments')
)
permission_comment_view = namespace.add_permission(
    name='comment_view', label=_('View comments')
)
