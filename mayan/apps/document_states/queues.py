from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from task_manager.classes import CeleryQueue

queue_document_states = CeleryQueue(
    name='document_states', label=_('Document states')
)
queue_document_states.add_task_type(
    name='document_states.tasks.task_launch_all_workflows',
    label=_('Launch all workflows')
)
