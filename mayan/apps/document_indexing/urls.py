from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIDocumentIndexListView, APIIndexListView,
    APIIndexNodeInstanceDocumentListView, APIIndexTemplateListView,
    APIIndexTemplateView, APIIndexView
)
from .views import (
    DocumentIndexNodeListView, IndexInstanceNodeView, IndexListView,
    RebuildIndexesView, SetupIndexDocumentTypesView, SetupIndexCreateView,
    SetupIndexDeleteView, SetupIndexEditView, SetupIndexListView,
    SetupIndexTreeTemplateListView, TemplateNodeCreateView,
    TemplateNodeDeleteView, TemplateNodeEditView
)

urlpatterns = [
    url(
        r'^setup/index/list/$', SetupIndexListView.as_view(),
        name='index_setup_list'
    ),
    url(
        r'^setup/index/create/$', SetupIndexCreateView.as_view(),
        name='index_setup_create'
    ),
    url(
        r'^setup/index/(?P<pk>\d+)/edit/$', SetupIndexEditView.as_view(),
        name='index_setup_edit'
    ),
    url(
        r'^setup/index/(?P<pk>\d+)/delete/$', SetupIndexDeleteView.as_view(),
        name='index_setup_delete'
    ),
    url(
        r'^setup/index/(?P<pk>\d+)/template/$',
        SetupIndexTreeTemplateListView.as_view(), name='index_setup_view'
    ),
    url(
        r'^setup/index/(?P<pk>\d+)/document_types/$',
        SetupIndexDocumentTypesView.as_view(),
        name='index_setup_document_types'
    ),
    url(
        r'^setup/template/node/(?P<pk>\d+)/create/child/$',
        TemplateNodeCreateView.as_view(), name='template_node_create'
    ),
    url(
        r'^setup/template/node/(?P<pk>\d+)/edit/$',
        TemplateNodeEditView.as_view(), name='template_node_edit'
    ),
    url(
        r'^setup/template/node/(?P<pk>\d+)/delete/$',
        TemplateNodeDeleteView.as_view(), name='template_node_delete'
    ),

    url(r'^index/list/$', IndexListView.as_view(), name='index_list'),
    url(
        r'^instance/node/(?P<pk>\d+)/$', IndexInstanceNodeView.as_view(),
        name='index_instance_node_view'
    ),

    url(
        r'^rebuild/all/$', RebuildIndexesView.as_view(),
        name='rebuild_index_instances'
    ),
    url(
        r'^list/for/document/(?P<pk>\d+)/$',
        DocumentIndexNodeListView.as_view(), name='document_index_list'
    ),
]

api_urls = [
    url(
        r'^index/node/(?P<pk>[0-9]+)/documents/$',
        APIIndexNodeInstanceDocumentListView.as_view(),
        name='index-node-documents'
    ),
    url(
        r'^index/template/(?P<pk>[0-9]+)/$', APIIndexTemplateView.as_view(),
        name='index-template-detail'
    ),
    url(
        r'^indexes/(?P<pk>[0-9]+)/$', APIIndexView.as_view(),
        name='index-detail'
    ),
    url(
        r'^index/(?P<pk>[0-9]+)/template/$',
        APIIndexTemplateListView.as_view(), name='index-template-detail'
    ),
    url(r'^indexes/$', APIIndexListView.as_view(), name='index-list'),
    url(
        r'^document/(?P<pk>[0-9]+)/indexes/$',
        APIDocumentIndexListView.as_view(), name='document-index-list'
    ),
]
