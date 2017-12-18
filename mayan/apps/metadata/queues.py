from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from task_manager.classes import CeleryQueue

queue_metadata = CeleryQueue(
    name='metadata', label=_('Metadata')
)
queue_metadata.add_task_type(
    name='metadata.tasks.task_remove_metadata_type',
    label=_('Remove metadata type')
)
queue_metadata.add_task_type(
    name='metadata.tasks.task_add_required_metadata_type',
    label=_('Add required metadata type')
)
