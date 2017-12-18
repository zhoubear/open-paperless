from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('cabinets', _('Cabinets'))

# Translators: this refers to the permission that will allow users to add
# documents to cabinets.
permission_cabinet_add_document = namespace.add_permission(
    name='cabinet_add_document', label=_('Add documents to cabinets')
)
permission_cabinet_create = namespace.add_permission(
    name='cabinet_create', label=_('Create cabinets')
)
permission_cabinet_delete = namespace.add_permission(
    name='cabinet_delete', label=_('Delete cabinets')
)
permission_cabinet_edit = namespace.add_permission(
    name='cabinet_edit', label=_('Edit cabinets')
)
permission_cabinet_remove_document = namespace.add_permission(
    name='cabinet_remove_document', label=_('Remove documents from cabinets')
)
permission_cabinet_view = namespace.add_permission(
    name='cabinet_view', label=_('View cabinets')
)
