from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIDocumentCabinetListView, APICabinetDocumentListView,
    APICabinetDocumentView, APICabinetListView, APICabinetView
)
from .views import (
    DocumentAddToCabinetView, DocumentCabinetListView,
    DocumentRemoveFromCabinetView, CabinetChildAddView, CabinetCreateView,
    CabinetDeleteView, CabinetDetailView, CabinetEditView, CabinetListView,
)

urlpatterns = [
    url(r'^list/$', CabinetListView.as_view(), name='cabinet_list'),
    url(
        r'^(?P<pk>\d+)/child/add/$', CabinetChildAddView.as_view(),
        name='cabinet_child_add'
    ),
    url(r'^create/$', CabinetCreateView.as_view(), name='cabinet_create'),
    url(
        r'^(?P<pk>\d+)/edit/$', CabinetEditView.as_view(), name='cabinet_edit'
    ),
    url(
        r'^(?P<pk>\d+)/delete/$', CabinetDeleteView.as_view(),
        name='cabinet_delete'
    ),
    url(r'^(?P<pk>\d+)/$', CabinetDetailView.as_view(), name='cabinet_view'),

    url(
        r'^document/(?P<pk>\d+)/cabinet/add/$',
        DocumentAddToCabinetView.as_view(), name='cabinet_add_document'
    ),
    url(
        r'^document/multiple/cabinet/add/$',
        DocumentAddToCabinetView.as_view(),
        name='cabinet_add_multiple_documents'
    ),
    url(
        r'^document/(?P<pk>\d+)/cabinet/remove/$',
        DocumentRemoveFromCabinetView.as_view(), name='document_cabinet_remove'
    ),
    url(
        r'^document/multiple/cabinet/remove/$',
        DocumentRemoveFromCabinetView.as_view(),
        name='multiple_document_cabinet_remove'
    ),
    url(
        r'^document/(?P<pk>\d+)/cabinet/list/$',
        DocumentCabinetListView.as_view(), name='document_cabinet_list'
    ),
]

api_urls = [
    url(
        r'^cabinets/(?P<pk>[0-9]+)/documents/(?P<document_pk>[0-9]+)/$',
        APICabinetDocumentView.as_view(), name='cabinet-document'
    ),
    url(
        r'^cabinets/(?P<pk>[0-9]+)/documents/$',
        APICabinetDocumentListView.as_view(), name='cabinet-document-list'
    ),
    url(
        r'^cabinets/(?P<pk>[0-9]+)/$', APICabinetView.as_view(),
        name='cabinet-detail'
    ),
    url(r'^cabinets/$', APICabinetListView.as_view(), name='cabinet-list'),
    url(
        r'^documents/(?P<pk>[0-9]+)/cabinets/$',
        APIDocumentCabinetListView.as_view(), name='document-cabinet-list'
    ),
]
