from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIResolvedSmartLinkView, APIResolvedSmartLinkDocumentListView,
    APIResolvedSmartLinkListView, APISmartLinkListView, APISmartLinkView,
    APISmartLinkConditionListView, APISmartLinkConditionView
)
from .views import (
    DocumentSmartLinkListView, ResolvedSmartLinkView,
    SetupSmartLinkDocumentTypesView, SmartLinkConditionListView,
    SmartLinkConditionCreateView, SmartLinkConditionEditView,
    SmartLinkConditionDeleteView, SmartLinkCreateView, SmartLinkDeleteView,
    SmartLinkEditView, SmartLinkListView
)

urlpatterns = [
    url(
        r'^document/(?P<pk>\d+)/list/$', DocumentSmartLinkListView.as_view(),
        name='smart_link_instances_for_document'
    ),
    url(
        r'^document/(?P<document_pk>\d+)/(?P<smart_link_pk>\d+)/$',
        ResolvedSmartLinkView.as_view(), name='smart_link_instance_view'
    ),

    url(
        r'^setup/list/$', SmartLinkListView.as_view(), name='smart_link_list'
    ),
    url(
        r'^setup/create/$', SmartLinkCreateView.as_view(),
        name='smart_link_create'
    ),
    url(
        r'^setup/(?P<pk>\d+)/delete/$',
        SmartLinkDeleteView.as_view(), name='smart_link_delete'
    ),
    url(
        r'^setup/(?P<pk>\d+)/edit/$', SmartLinkEditView.as_view(),
        name='smart_link_edit'
    ),
    url(
        r'^setup/(?P<pk>\d+)/document_types/$',
        SetupSmartLinkDocumentTypesView.as_view(),
        name='smart_link_document_types'
    ),

    url(
        r'^setup/(?P<pk>\d+)/condition/list/$',
        SmartLinkConditionListView.as_view(), name='smart_link_condition_list'
    ),
    url(
        r'^setup/(?P<pk>\d+)/condition/create/$',
        SmartLinkConditionCreateView.as_view(),
        name='smart_link_condition_create'
    ),
    url(
        r'^setup/smart_link/condition/(?P<pk>\d+)/edit/$',
        SmartLinkConditionEditView.as_view(), name='smart_link_condition_edit'
    ),
    url(
        r'^setup/smart_link/condition/(?P<pk>\d+)/delete/$',
        SmartLinkConditionDeleteView.as_view(),
        name='smart_link_condition_delete'
    ),
]

api_urls = [
    url(
        r'^smart_links/$', APISmartLinkListView.as_view(),
        name='smartlink-list'
    ),
    url(
        r'^smart_links/(?P<pk>[0-9]+)/$', APISmartLinkView.as_view(),
        name='smartlink-detail'
    ),
    url(
        r'^smart_links/(?P<pk>[0-9]+)/conditions/$',
        APISmartLinkConditionListView.as_view(), name='smartlinkcondition-list'
    ),
    url(
        r'^smart_links/(?P<pk>[0-9]+)/conditions/(?P<condition_pk>[0-9]+)/$',
        APISmartLinkConditionView.as_view(),
        name='smartlinkcondition-detail'
    ),
    url(
        r'^documents/(?P<pk>[0-9]+)/resolved_smart_links/$',
        APIResolvedSmartLinkListView.as_view(),
        name='resolvedsmartlink-list'
    ),
    url(
        r'^documents/(?P<pk>[0-9]+)/resolved_smart_links/(?P<smart_link_pk>[0-9]+)/$',
        APIResolvedSmartLinkView.as_view(),
        name='resolvedsmartlink-detail'
    ),
    url(
        r'^documents/(?P<pk>[0-9]+)/resolved_smart_links/(?P<smart_link_pk>[0-9]+)/documents/$',
        APIResolvedSmartLinkDocumentListView.as_view(),
        name='resolvedsmartlinkdocument-list'
    ),
]
