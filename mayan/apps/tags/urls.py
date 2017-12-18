from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIDocumentTagView, APIDocumentTagListView, APITagDocumentListView,
    APITagListView, APITagView
)
from .views import (
    DocumentTagListView, TagAttachActionView, TagCreateView,
    TagDeleteActionView, TagEditView, TagListView, TagRemoveActionView,
    TagTaggedItemListView
)

urlpatterns = [
    url(r'^list/$', TagListView.as_view(), name='tag_list'),
    url(r'^create/$', TagCreateView.as_view(), name='tag_create'),
    url(
        r'^(?P<pk>\d+)/delete/$', TagDeleteActionView.as_view(),
        name='tag_delete'
    ),
    url(r'^(?P<pk>\d+)/edit/$', TagEditView.as_view(), name='tag_edit'),
    url(
        r'^(?P<pk>\d+)/documents/$', TagTaggedItemListView.as_view(),
        name='tag_tagged_item_list'
    ),
    url(
        r'^multiple/delete/$', TagDeleteActionView.as_view(),
        name='tag_multiple_delete'
    ),

    url(
        r'^multiple/remove/document/(?P<pk>\d+)/$',
        TagRemoveActionView.as_view(),
        name='single_document_multiple_tag_remove'
    ),
    url(
        r'^multiple/remove/document/multiple/$',
        TagRemoveActionView.as_view(),
        name='multiple_documents_selection_tag_remove'
    ),

    url(
        r'^selection/attach/document/(?P<pk>\d+)/$',
        TagAttachActionView.as_view(), name='tag_attach'
    ),
    url(
        r'^selection/attach/document/multiple/$',
        TagAttachActionView.as_view(), name='multiple_documents_tag_attach'
    ),

    url(
        r'^document/(?P<pk>\d+)/tags/$', DocumentTagListView.as_view(),
        name='document_tags'
    ),
]

api_urls = [
    url(
        r'^tags/(?P<pk>[0-9]+)/documents/$', APITagDocumentListView.as_view(),
        name='tag-document-list'
    ),
    url(r'^tags/(?P<pk>[0-9]+)/$', APITagView.as_view(), name='tag-detail'),
    url(r'^tags/$', APITagListView.as_view(), name='tag-list'),
    url(
        r'^documents/(?P<document_pk>[0-9]+)/tags/$',
        APIDocumentTagListView.as_view(), name='document-tag-list'
    ),
    url(
        r'^documents/(?P<document_pk>[0-9]+)/tags/(?P<pk>[0-9]+)/$',
        APIDocumentTagView.as_view(), name='document-tag-detail'
    ),
]
