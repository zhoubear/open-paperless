from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('statistics', _('Statistics'))

permission_statistics_view = namespace.add_permission(
    name='statistics_view', label=_('View statistics')
)
