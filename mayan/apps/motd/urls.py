from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import APIMessageListView, APIMessageView
from .views import (
    MessageCreateView, MessageDeleteView, MessageEditView, MessageListView
)

urlpatterns = [
    url(r'^list/$', MessageListView.as_view(), name='message_list'),
    url(r'^create/$', MessageCreateView.as_view(), name='message_create'),
    url(
        r'^(?P<pk>\d+)/edit/$', MessageEditView.as_view(), name='message_edit'
    ),
    url(
        r'^(?P<pk>\d+)/delete/$', MessageDeleteView.as_view(),
        name='message_delete'
    ),
]

api_urls = [
    url(r'^messages/$', APIMessageListView.as_view(), name='message-list'),
    url(
        r'^messages/(?P<pk>[0-9]+)/$', APIMessageView.as_view(),
        name='message-detail'
    ),
]
