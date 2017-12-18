from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('document_parsing', _('Document parsing'))

permission_content_view = namespace.add_permission(
    name='content_view', label=_('View the content of a document')
)

permission_parse_document = namespace.add_permission(
    name='parse_document', label=_('Parse the content of a document')
)
