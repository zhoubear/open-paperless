from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from task_manager.classes import CeleryQueue

queue_mailing = CeleryQueue(
    name='mailing', label=_('Mailing')
)
queue_mailing.add_task_type(
    name='mailer.tasks.task_send_document',
    label=_('Send document')
)
