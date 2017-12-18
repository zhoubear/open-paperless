from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('task_manager', _('Task manager'))

permission_task_view = namespace.add_permission(
    name='task_view', label=_('View tasks')
)
