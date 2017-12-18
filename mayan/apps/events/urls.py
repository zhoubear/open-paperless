from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIEventListView, APIEventTypeListView, APIObjectEventListView
)
from .views import EventListView, ObjectEventListView, VerbEventListView

urlpatterns = [
    url(r'^all/$', EventListView.as_view(), name='events_list'),
    url(
        r'^for/(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_id>\d+)/$',
        ObjectEventListView.as_view(), name='events_for_object'
    ),
    url(
        r'^by_verb/(?P<verb>[\w\-]+)/$', VerbEventListView.as_view(),
        name='events_by_verb'
    ),
]

api_urls = [
    url(r'^types/$', APIEventTypeListView.as_view(), name='event-type-list'),
    url(r'^events/$', APIEventListView.as_view(), name='event-list'),
    url(
        r'^object/(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_id>\d+)/events/$',
        APIObjectEventListView.as_view(), name='object-event-list'
    ),
]
