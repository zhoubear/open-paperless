from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from task_manager.classes import CeleryQueue

queue_checkouts_periodic = CeleryQueue(
    name='checkouts_periodic', label=_('Checkouts periodic'), transient=True
)
queue_checkouts_periodic.add_task_type(
    name='task_check_expired_check_outs',
    label=_('Check expired checkouts')
)
