from __future__ import unicode_literals

from django.conf.urls import url

from .views import (
    NamespaceDetailView, NamespaceListView, StatisticDetailView,
    StatisticQueueView
)

urlpatterns = [
    url(r'^$', NamespaceListView.as_view(), name='namespace_list'),
    url(
        r'^namespace/(?P<slug>[\w-]+)/details/$',
        NamespaceDetailView.as_view(), name='namespace_details'
    ),
    url(
        r'^(?P<slug>[\w-]+)/view/$', StatisticDetailView.as_view(),
        name='statistic_detail'
    ),
    url(
        r'^(?P<slug>[\w-]+)/queue/$', StatisticQueueView.as_view(),
        name='statistic_queue'
    ),
]
