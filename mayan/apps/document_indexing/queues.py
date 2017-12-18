from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from common.queues import queue_tools
from task_manager.classes import CeleryQueue

queue_indexing = CeleryQueue(name='indexing', label=_('Indexing'))

queue_indexing.add_task_type(
    name='document_indexing.tasks.task_delete_empty',
    label=_('Delete empty index nodes')
)
queue_indexing.add_task_type(
    name='document_indexing.tasks.task_remove_document',
    label=_('Remove document')
)
queue_indexing.add_task_type(
    name='document_indexing.tasks.task_index_document',
    label=_('Index document')
)
queue_tools.add_task_type(
    name='document_indexing.tasks.task_rebuild_index',
    label=_('Rebuild index')
)
