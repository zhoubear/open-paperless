from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from common.queues import queue_tools
from task_manager.classes import CeleryQueue

queue_signatures = CeleryQueue(name='signatures', label=_('Signatures'))
queue_signatures.add_task_type(
    name='document_signatures.tasks.task_verify_key_signatures',
    label=_('Verify key signatures')
)
queue_signatures.add_task_type(
    name='document_signatures.tasks.task_unverify_key_signatures',
    label=_('Unverify key signatures')
)
queue_signatures.add_task_type(
    name='document_signatures.tasks.task_verify_document_version',
    label=_('Verify document version')
)

queue_tools.add_task_type(
    name='document_signatures.tasks.task_verify_missing_embedded_signature',
    label=_('Verify missing embedded signature')
)
