from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import APIDocumentPageContentView
from .views import (
    DocumentContentView, DocumentContentDownloadView,
    DocumentParsingErrorsListView, DocumentSubmitView, DocumentTypeSubmitView,
    ParseErrorListView
)

urlpatterns = [
    url(
        r'^documents/(?P<pk>\d+)/content/$', DocumentContentView.as_view(),
        name='document_content'
    ),
    url(
        r'^documents/(?P<pk>\d+)/content/download/$',
        DocumentContentDownloadView.as_view(), name='document_content_download'
    ),
    url(
        r'^document_types/submit/$', DocumentTypeSubmitView.as_view(),
        name='document_type_submit'
    ),
    url(
        r'^documents/(?P<pk>\d+)/submit/$', DocumentSubmitView.as_view(),
        name='document_submit'
    ),
    url(
        r'^documents/multiple/submit/$', DocumentSubmitView.as_view(),
        name='document_submit_multiple'
    ),
    url(
        r'^documents/(?P<pk>\d+)/errors/$',
        DocumentParsingErrorsListView.as_view(),
        name='document_parsing_error_list'
    ),
    url(r'^errors/all/$', ParseErrorListView.as_view(), name='error_list'),
]

api_urls = [
    url(
        r'^page/(?P<pk>\d+)/content/$', APIDocumentPageContentView.as_view(),
        name='document-page-content-view'
    ),
]
