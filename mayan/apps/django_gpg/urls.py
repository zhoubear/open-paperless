from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import APIKeyListView, APIKeyView
from .views import (
    KeyDeleteView, KeyDetailView, KeyDownloadView, KeyQueryView,
    KeyQueryResultView, KeyReceive, KeyUploadView, PrivateKeyListView,
    PublicKeyListView
)

urlpatterns = [
    url(
        r'^(?P<pk>\d+)/$', KeyDetailView.as_view(), name='key_detail'
    ),
    url(
        r'^(?P<pk>\d+)/delete/$', KeyDeleteView.as_view(), name='key_delete'
    ),
    url(
        r'^(?P<pk>\d+)/download/$', KeyDownloadView.as_view(),
        name='key_download'
    ),
    url(
        r'^list/private/$', PrivateKeyListView.as_view(),
        name='key_private_list'
    ),
    url(
        r'^list/public/$', PublicKeyListView.as_view(), name='key_public_list'
    ),
    url(
        r'^upload/$', KeyUploadView.as_view(), name='key_upload'
    ),
    url(r'^query/$', KeyQueryView.as_view(), name='key_query'),
    url(
        r'^query/results/$', KeyQueryResultView.as_view(),
        name='key_query_results'
    ),
    url(
        r'^receive/(?P<key_id>.+)/$', KeyReceive.as_view(), name='key_receive'
    ),
]

api_urls = [
    url(
        r'^keys/(?P<pk>[0-9]+)/$', APIKeyView.as_view(),
        name='key-detail'
    ),
    url(r'^keys/$', APIKeyListView.as_view(), name='key-list'),
]
