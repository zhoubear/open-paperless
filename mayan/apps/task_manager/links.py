from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Link

from .permissions import permission_task_view

link_task_manager = Link(
    icon='fa fa-braille', permissions=(permission_task_view,),
    text=_('Task manager'), view='task_manager:queue_list'
)
link_queue_list = Link(
    icon='fa fa-braille', permissions=(permission_task_view,),
    text=_('Background task queues'), view='task_manager:queue_list'
)
link_queue_active_task_list = Link(
    args='resolved_object.name', permissions=(permission_task_view,),
    text=_('Active tasks'), view='task_manager:queue_active_task_list'
)
link_queue_reserved_task_list = Link(
    args='resolved_object.name', permissions=(permission_task_view,),
    text=_('Reserved tasks'), view='task_manager:queue_reserved_task_list'
)
link_queue_scheduled_task_list = Link(
    args='resolved_object.name', permissions=(permission_task_view,),
    text=_('Scheduled tasks'), view='task_manager:queue_scheduled_task_list'
)
