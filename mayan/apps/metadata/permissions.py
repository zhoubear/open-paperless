from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('metadata', _('Metadata'))
permission_metadata_document_edit = namespace.add_permission(
    name='metadata_document_edit', label=_('Edit a document\'s metadata')
)
permission_metadata_document_add = namespace.add_permission(
    name='metadata_document_add', label=_('Add metadata to a document'))
permission_metadata_document_remove = namespace.add_permission(
    name='metadata_document_remove',
    label=_('Remove metadata from a document')
)
permission_metadata_document_view = namespace.add_permission(
    name='metadata_document_view', label=_('View metadata from a document')
)

setup_namespace = PermissionNamespace('metadata_setup', _('Metadata setup'))
permission_metadata_type_edit = setup_namespace.add_permission(
    name='metadata_type_edit', label=_('Edit metadata types')
)
permission_metadata_type_create = setup_namespace.add_permission(
    name='metadata_type_create', label=_('Create new metadata types')
)
permission_metadata_type_delete = setup_namespace.add_permission(
    name='metadata_type_delete', label=_('Delete metadata types')
)
permission_metadata_type_view = setup_namespace.add_permission(
    name='metadata_type_view', label=_('View metadata types')
)
