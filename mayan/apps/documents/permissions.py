from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('documents', _('Documents'))

permission_document_create = namespace.add_permission(
    name='document_create', label=_('Create documents')
)
permission_document_delete = namespace.add_permission(
    name='document_delete', label=_('Delete documents')
)
permission_document_trash = namespace.add_permission(
    name='document_trash', label=_('Trash documents')
)
permission_document_download = namespace.add_permission(
    name='document_download', label=_('Download documents')
)
permission_document_edit = namespace.add_permission(
    name='document_edit', label=_('Edit documents')
)
permission_document_new_version = namespace.add_permission(
    name='document_new_version', label=_('Create new document versions')
)
permission_document_properties_edit = namespace.add_permission(
    name='document_properties_edit', label=_('Edit document properties')
)
permission_document_print = namespace.add_permission(
    name='document_print', label=_('Print documents')
)
permission_document_restore = namespace.add_permission(
    name='document_restore', label=_('Restore trashed document')
)
permission_document_tools = namespace.add_permission(
    name='document_tools', label=_('Execute document modifying tools')
)
permission_document_version_revert = namespace.add_permission(
    name='document_version_revert',
    label=_('Revert documents to a previous version')
)
permission_document_version_view = namespace.add_permission(
    name='document_version_view',
    label=_('View documents\' versions list')
)
permission_document_view = namespace.add_permission(
    name='document_view', label=_('View documents')
)
permission_empty_trash = namespace.add_permission(
    name='document_empty_trash', label=_('Empty trash')
)

# TODO: rename 'document_setup' to 'document_types' on the next major version
setup_namespace = PermissionNamespace(
    'documents_setup', label=_('Document types')
)
permission_document_type_create = setup_namespace.add_permission(
    name='document_type_create', label=_('Create document types')
)
permission_document_type_delete = setup_namespace.add_permission(
    name='document_type_delete', label=_('Delete document types')
)
permission_document_type_edit = setup_namespace.add_permission(
    name='document_type_edit', label=_('Edit document types')
)
permission_document_type_view = setup_namespace.add_permission(
    name='document_type_view', label=_('View document types')
)
