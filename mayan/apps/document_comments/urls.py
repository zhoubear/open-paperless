from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import APICommentListView, APICommentView
from .views import (
    DocumentCommentCreateView, DocumentCommentDeleteView,
    DocumentCommentListView
)

urlpatterns = [
    url(
        r'^comment/(?P<pk>\d+)/delete/$', DocumentCommentDeleteView.as_view(),
        name='comment_delete'
    ),
    url(
        r'^(?P<pk>\d+)/comment/add/$', DocumentCommentCreateView.as_view(),
        name='comment_add'
    ),
    url(
        r'^(?P<pk>\d+)/comment/list/$',
        DocumentCommentListView.as_view(), name='comments_for_document'
    ),
]

api_urls = [
    url(
        r'^document/(?P<document_pk>[0-9]+)/comments/$',
        APICommentListView.as_view(), name='comment-list'
    ),
    url(
        r'^document/(?P<document_pk>[0-9]+)/comments/(?P<comment_pk>[0-9]+)/$',
        APICommentView.as_view(), name='comment-detail'
    ),
]
