from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('document_indexing', _('Indexing'))

permission_document_indexing_create = namespace.add_permission(
    name='document_index_create', label=_('Create new document indexes')
)
permission_document_indexing_edit = namespace.add_permission(
    name='document_index_edit', label=_('Edit document indexes')
)
permission_document_indexing_delete = namespace.add_permission(
    name='document_index_delete', label=_('Delete document indexes')
)
permission_document_indexing_view = namespace.add_permission(
    name='document_index_view', label=_('View document indexes')
)
permission_document_indexing_rebuild = namespace.add_permission(
    name='document_rebuild_indexes', label=_('Rebuild document indexes')
)
