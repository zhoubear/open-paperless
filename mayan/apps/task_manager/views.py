from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from common.generics import SingleObjectListView

from .classes import CeleryQueue
from .permissions import permission_task_view


class QueueListView(SingleObjectListView):
    extra_context = {
        'hide_object': True,
        'title': _('Background task queues'),
    }
    view_permission = permission_task_view

    def get_object_list(self):
        return CeleryQueue.all()


class QueueActiveTaskListView(SingleObjectListView):
    view_permission = permission_task_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'object': self.get_object(),
            'title': _('Active tasks in queue: %s') % self.get_object()
        }

    def get_object(self):
        return CeleryQueue.get(queue_name=self.kwargs['queue_name'])

    def get_object_list(self):
        try:
            return self.get_task_list()
        except Exception as exception:
            messages.error(
                self.request,
                _('Unable to retrieve task list; %s') % exception
            )
            return ()

    def get_task_list(self):
        return self.get_object().get_active_tasks()


class QueueScheduledTaskListView(QueueActiveTaskListView):
    def get_extra_context(self):
        return {
            'hide_object': True,
            'object': self.get_object(),
            'title': _('Scheduled tasks in queue: %s') % self.get_object()
        }

    def get_task_list(self):
        return self.get_object().get_scheduled_tasks()


class QueueReservedTaskListView(QueueActiveTaskListView):
    def get_extra_context(self):
        return {
            'hide_object': True,
            'object': self.get_object(),
            'title': _('Reserved tasks in queue: %s') % self.get_object()
        }

    def get_task_list(self):
        return self.get_object().get_reserved_tasks()
