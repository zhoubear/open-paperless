from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from common import (
    MayanAppConfig, menu_object, menu_secondary, menu_tools
)
from common.widgets import two_state_template
from navigation import SourceColumn

from .classes import CeleryQueue, Task
from .links import (
    link_queue_list, link_queue_active_task_list,
    link_queue_scheduled_task_list, link_queue_reserved_task_list,
    link_task_manager
)


class TaskManagerApp(MayanAppConfig):
    app_namespace = 'task_manager'
    app_url = 'task_manager'
    has_tests = True
    name = 'task_manager'
    verbose_name = _('Task manager')

    def ready(self):
        super(TaskManagerApp, self).ready()

        SourceColumn(
            source=CeleryQueue, label=_('Label'), attribute='label'
        )
        SourceColumn(
            source=CeleryQueue, label=_('Name'), attribute='name'
        )
        SourceColumn(
            source=CeleryQueue, label=_('Default queue?'),
            func=lambda context: two_state_template(
                context['object'].is_default_queue
            )
        )
        SourceColumn(
            source=CeleryQueue, label=_('Is transient?'),
            func=lambda context: two_state_template(
                context['object'].is_transient
            )
        )
        SourceColumn(
            source=Task, label=_('Type'), attribute='task_type'
        )
        SourceColumn(
            source=Task, label=_('Start time'), attribute='get_time_started'
        )
        SourceColumn(
            source=Task, label=_('Host'),
            func=lambda context: context['object'].kwargs['hostname']
        )
        SourceColumn(
            source=Task, label=_('Acknowledged'),
            func=lambda context: two_state_template(
                context['object'].kwargs['acknowledged']
            )
        )
        SourceColumn(
            source=Task, label=_('Arguments'),
            func=lambda context: context['object'].kwargs['args']
        )
        SourceColumn(
            source=Task, label=_('Keyword arguments'),
            func=lambda context: context['object'].kwargs['kwargs']
        )
        SourceColumn(
            source=Task, label=_('Worker process ID'),
            func=lambda context: context['object'].kwargs['worker_pid']
        )

        menu_object.bind_links(
            links=(
                link_queue_active_task_list, link_queue_scheduled_task_list,
                link_queue_reserved_task_list,
            ), sources=(CeleryQueue,)
        )

        menu_secondary.bind_links(
            links=(link_queue_list,),
            sources=(CeleryQueue, Task, 'task_manager:queue_list')
        )

        menu_tools.bind_links(links=(link_task_manager,))
