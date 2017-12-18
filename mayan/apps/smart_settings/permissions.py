from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('smart_settings', _('Smart settings'))

permission_settings_view = namespace.add_permission(
    name='permission_settings_view', label=_('View settings')
)
