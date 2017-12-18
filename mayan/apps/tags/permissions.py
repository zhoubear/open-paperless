from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('tags', _('Tags'))

permission_tag_create = namespace.add_permission(
    name='tag_create', label=_('Create new tags')
)
permission_tag_delete = namespace.add_permission(
    name='tag_delete', label=_('Delete tags')
)
permission_tag_view = namespace.add_permission(
    name='tag_view', label=_('View tags')
)
permission_tag_edit = namespace.add_permission(
    name='tag_edit', label=_('Edit tags')
)
permission_tag_attach = namespace.add_permission(
    name='tag_attach', label=_('Attach tags to documents')
)
permission_tag_remove = namespace.add_permission(
    name='tag_remove', label=_('Remove tags from documents')
)
