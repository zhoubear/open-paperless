from __future__ import unicode_literals

from django.conf.urls import url

from .views import (
    QueueListView, QueueActiveTaskListView, QueueScheduledTaskListView,
    QueueReservedTaskListView
)


urlpatterns = [
    url(
        r'^queues/$', QueueListView.as_view(),
        name='queue_list'
    ),
    url(
        r'^queues/(?P<queue_name>[-\w]+)/tasks/active/$',
        QueueActiveTaskListView.as_view(), name='queue_active_task_list'
    ),
    url(
        r'^queues/(?P<queue_name>[-\w]+)/tasks/scheduled/$',
        QueueScheduledTaskListView.as_view(), name='queue_scheduled_task_list'
    ),
    url(
        r'^queues/(?P<queue_name>[-\w]+)/tasks/reserved/$',
        QueueReservedTaskListView.as_view(), name='queue_reserved_task_list'
    ),
]
