from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('common', _('Common'))

permission_error_log_view = namespace.add_permission(
    name='error_log_view', label=_('View error log')
)
