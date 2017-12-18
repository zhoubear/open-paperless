from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from task_manager.classes import CeleryQueue

queue_default = CeleryQueue(
    name='default', label=_('Default'), is_default_queue=True
)
queue_tools = CeleryQueue(name='tools', label=_('Tools'))
queue_common_periodic = CeleryQueue(
    name='common_periodic', label=_('Common periodic'), transient=True
)
queue_common_periodic.add_task_type(
    name='common.tasks.task_delete_stale_uploads',
    label=_('Delete stale uploads')
)
