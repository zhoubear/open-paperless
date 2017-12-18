from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('checkouts', _('Document checkout'))

permission_document_checkin = namespace.add_permission(
    name='checkin_document', label=_('Check in documents')
)
permission_document_checkin_override = namespace.add_permission(
    name='checkin_document_override', label=_('Forcefully check in documents')
)
permission_document_checkout = namespace.add_permission(
    name='checkout_document', label=_('Check out documents')
)
permission_document_checkout_detail_view = namespace.add_permission(
    name='checkout_detail_view', label=_('Check out details view')
)
