from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIDeletedDocumentListView, APIDeletedDocumentRestoreView,
    APIDeletedDocumentView, APIDocumentDownloadView, APIDocumentView,
    APIDocumentListView, APIDocumentVersionDownloadView,
    APIDocumentPageImageView, APIDocumentPageView,
    APIDocumentTypeDocumentListView, APIDocumentTypeListView,
    APIDocumentTypeView, APIDocumentVersionsListView,
    APIDocumentVersionPageListView, APIDocumentVersionView,
    APIRecentDocumentListView
)
from .views import (
    ClearImageCacheView, DeletedDocumentDeleteView,
    DeletedDocumentDeleteManyView, DeletedDocumentListView,
    DocumentDocumentTypeEditView, DocumentDownloadFormView,
    DocumentDownloadView, DocumentDuplicatesListView, DocumentEditView,
    DocumentListView, DocumentPageListView, DocumentPageNavigationFirst,
    DocumentPageNavigationLast, DocumentPageNavigationNext,
    DocumentPageNavigationPrevious, DocumentPageRotateLeftView,
    DocumentPageRotateRightView, DocumentPageView, DocumentPageViewResetView,
    DocumentPageZoomInView, DocumentPageZoomOutView, DocumentPreviewView,
    DocumentPrint, DocumentRestoreView, DocumentRestoreManyView,
    DocumentTransformationsClearView, DocumentTransformationsCloneView,
    DocumentTrashView, DocumentTrashManyView, DocumentTypeCreateView,
    DocumentTypeDeleteView, DocumentTypeDocumentListView,
    DocumentTypeFilenameCreateView, DocumentTypeFilenameDeleteView,
    DocumentTypeFilenameEditView, DocumentTypeFilenameListView,
    DocumentTypeListView, DocumentTypeEditView, DocumentUpdatePageCountView,
    DocumentVersionDownloadFormView, DocumentVersionDownloadView,
    DocumentVersionListView, DocumentVersionRevertView, DocumentVersionView,
    DocumentView, DuplicatedDocumentListView, EmptyTrashCanView,
    RecentDocumentListView, ScanDuplicatedDocuments
)


urlpatterns = [
    url(r'^list/$', DocumentListView.as_view(), name='document_list'),
    url(
        r'^list/recent/$', RecentDocumentListView.as_view(),
        name='document_list_recent'
    ),
    url(
        r'^list/deleted/$', DeletedDocumentListView.as_view(),
        name='document_list_deleted'
    ),
    url(
        r'^list/duplicated/$',
        DuplicatedDocumentListView.as_view(),
        name='duplicated_document_list'
    ),
    url(
        r'^(?P<pk>\d+)/preview/$', DocumentPreviewView.as_view(),
        name='document_preview'
    ),
    url(
        r'^(?P<pk>\d+)/properties/$', DocumentView.as_view(),
        name='document_properties'
    ),
    url(
        r'^(?P<pk>\d+)/duplicates/$', DocumentDuplicatesListView.as_view(),
        name='document_duplicates_list'
    ),
    url(
        r'^(?P<pk>\d+)/restore/$', DocumentRestoreView.as_view(),
        name='document_restore'
    ),
    url(
        r'^multiple/restore/$', DocumentRestoreManyView.as_view(),
        name='document_multiple_restore'
    ),
    url(
        r'^(?P<pk>\d+)/delete/$', DeletedDocumentDeleteView.as_view(),
        name='document_delete'
    ),
    url(
        r'^multiple/delete/$', DeletedDocumentDeleteManyView.as_view(),
        name='document_multiple_delete'
    ),
    url(
        r'^(?P<pk>\d+)/type/$', DocumentDocumentTypeEditView.as_view(),
        name='document_document_type_edit'
    ),
    url(
        r'^multiple/type/$', DocumentDocumentTypeEditView.as_view(),
        name='document_multiple_document_type_edit'
    ),
    url(
        r'^(?P<pk>\d+)/trash/$', DocumentTrashView.as_view(),
        name='document_trash'
    ),
    url(
        r'^multiple/trash/$', DocumentTrashManyView.as_view(),
        name='document_multiple_trash'
    ),
    url(
        r'^(?P<pk>\d+)/edit/$', DocumentEditView.as_view(),
        name='document_edit'
    ),
    url(
        r'^(?P<pk>\d+)/print/$', DocumentPrint.as_view(),
        name='document_print'
    ),
    url(
        r'^(?P<pk>\d+)/reset_page_count/$',
        DocumentUpdatePageCountView.as_view(),
        name='document_update_page_count'
    ),
    url(
        r'^multiple/reset_page_count/$',
        DocumentUpdatePageCountView.as_view(),
        name='document_multiple_update_page_count'
    ),
    url(
        r'^(?P<pk>\d+)/download/form/$',
        DocumentDownloadFormView.as_view(), name='document_download_form'
    ),
    url(
        r'^(?P<pk>\d+)/download/$', DocumentDownloadView.as_view(),
        name='document_download'
    ),
    url(
        r'^multiple/download/form/$', DocumentDownloadFormView.as_view(),
        name='document_multiple_download_form'
    ),
    url(
        r'^multiple/download/$', DocumentDownloadView.as_view(),
        name='document_multiple_download'
    ),
    url(
        r'^(?P<pk>\d+)/clear_transformations/$',
        DocumentTransformationsClearView.as_view(),
        name='document_clear_transformations'
    ),
    url(
        r'^(?P<pk>\d+)/clone_transformations/$',
        DocumentTransformationsCloneView.as_view(),
        name='document_clone_transformations'
    ),
    url(
        r'^(?P<pk>\d+)/version/all/$', DocumentVersionListView.as_view(),
        name='document_version_list'
    ),
    url(
        r'^document/version/(?P<pk>\d+)/download/form/$',
        DocumentVersionDownloadFormView.as_view(),
        name='document_version_download_form'
    ),
    url(
        r'^document/version/(?P<pk>\d+)/$', DocumentVersionView.as_view(),
        name='document_version_view'
    ),
    url(
        r'^document/version/(?P<pk>\d+)/download/$',
        DocumentVersionDownloadView.as_view(), name='document_version_download'
    ),
    url(
        r'^document/version/(?P<pk>\d+)/revert/$',
        DocumentVersionRevertView.as_view(), name='document_version_revert'
    ),

    url(
        r'^(?P<pk>\d+)/pages/all/$', DocumentPageListView.as_view(),
        name='document_pages'
    ),

    url(
        r'^multiple/clear_transformations/$',
        DocumentTransformationsClearView.as_view(),
        name='document_multiple_clear_transformations'
    ),
    url(
        r'^cache/clear/$', ClearImageCacheView.as_view(),
        name='document_clear_image_cache'
    ),
    url(
        r'^trash_can/empty/$', EmptyTrashCanView.as_view(),
        name='trash_can_empty'
    ),

    url(
        r'^page/(?P<pk>\d+)/$', DocumentPageView.as_view(),
        name='document_page_view'
    ),
    url(
        r'^page/(?P<pk>\d+)/navigation/next/$',
        DocumentPageNavigationNext.as_view(),
        name='document_page_navigation_next'
    ),
    url(
        r'^page/(?P<pk>\d+)/navigation/previous/$',
        DocumentPageNavigationPrevious.as_view(),
        name='document_page_navigation_previous'
    ),
    url(
        r'^page/(?P<pk>\d+)/navigation/first/$',
        DocumentPageNavigationFirst.as_view(),
        name='document_page_navigation_first'
    ),
    url(
        r'^page/(?P<pk>\d+)/navigation/last/$',
        DocumentPageNavigationLast.as_view(),
        name='document_page_navigation_last'
    ),
    url(
        r'^page/(?P<pk>\d+)/zoom/in/$',
        DocumentPageZoomInView.as_view(), name='document_page_zoom_in'
    ),
    url(
        r'^page/(?P<pk>\d+)/zoom/out/$',
        DocumentPageZoomOutView.as_view(), name='document_page_zoom_out'
    ),
    url(
        r'^page/(?P<pk>\d+)/rotate/left/$',
        DocumentPageRotateLeftView.as_view(), name='document_page_rotate_left'
    ),
    url(
        r'^page/(?P<pk>\d+)/rotate/right/$',
        DocumentPageRotateRightView.as_view(),
        name='document_page_rotate_right'
    ),
    url(
        r'^page/(?P<pk>\d+)/reset/$', DocumentPageViewResetView.as_view(),
        name='document_page_view_reset'
    ),

    # Admin views
    url(
        r'^type/list/$', DocumentTypeListView.as_view(),
        name='document_type_list'
    ),
    url(
        r'^type/create/$', DocumentTypeCreateView.as_view(),
        name='document_type_create'
    ),
    url(
        r'^type/(?P<pk>\d+)/edit/$', DocumentTypeEditView.as_view(),
        name='document_type_edit'
    ),
    url(
        r'^type/(?P<pk>\d+)/delete/$', DocumentTypeDeleteView.as_view(),
        name='document_type_delete'
    ),
    url(
        r'^type/(?P<pk>\d+)/documents/$',
        DocumentTypeDocumentListView.as_view(),
        name='document_type_document_list'
    ),
    url(
        r'^type/(?P<pk>\d+)/filename/list/$',
        DocumentTypeFilenameListView.as_view(),
        name='document_type_filename_list'
    ),
    url(
        r'^type/filename/(?P<pk>\d+)/edit/$',
        DocumentTypeFilenameEditView.as_view(),
        name='document_type_filename_edit'
    ),
    url(
        r'^type/filename/(?P<pk>\d+)/delete/$',
        DocumentTypeFilenameDeleteView.as_view(),
        name='document_type_filename_delete'
    ),
    url(
        r'^type/(?P<pk>\d+)/filename/create/$',
        DocumentTypeFilenameCreateView.as_view(),
        name='document_type_filename_create'
    ),

    # Tools

    url(
        r'^tools/documents/duplicated/scan/$',
        ScanDuplicatedDocuments.as_view(),
        name='duplicated_document_scan'
    ),
]

api_urls = [
    url(r'^documents/$', APIDocumentListView.as_view(), name='document-list'),
    url(
        r'^documents/recent/$', APIRecentDocumentListView.as_view(),
        name='document-recent-list'
    ),
    url(
        r'^documents/(?P<pk>[0-9]+)/$', APIDocumentView.as_view(),
        name='document-detail'
    ),
    url(
        r'^documents/(?P<pk>[0-9]+)/download/$',
        APIDocumentDownloadView.as_view(), name='document-download'
    ),
    url(
        r'^documents/(?P<pk>[0-9]+)/versions/$',
        APIDocumentVersionsListView.as_view(), name='document-version-list'
    ),
    url(
        r'^documents/(?P<pk>[0-9]+)/versions/(?P<version_pk>[0-9]+)/$',
        APIDocumentVersionView.as_view(), name='documentversion-detail'
    ),
    url(
        r'^documents/(?P<pk>[0-9]+)/versions/(?P<version_pk>[0-9]+)/pages/$',
        APIDocumentVersionPageListView.as_view(), name='documentversion-page-list'
    ),
    url(
        r'^documents/(?P<pk>[0-9]+)/versions/(?P<version_pk>[0-9]+)/download/$',
        APIDocumentVersionDownloadView.as_view(),
        name='documentversion-download'
    ),
    url(
        r'^documents/(?P<pk>[0-9]+)/versions/(?P<version_pk>[0-9]+)/pages/(?P<page_pk>[0-9]+)$',
        APIDocumentPageView.as_view(), name='documentpage-detail'
    ),
    url(
        r'^documents/(?P<pk>[0-9]+)/versions/(?P<version_pk>[0-9]+)/pages/(?P<page_pk>[0-9]+)/image/$',
        APIDocumentPageImageView.as_view(), name='documentpage-image'
    ),
    url(
        r'^document_types/(?P<pk>[0-9]+)/documents/$',
        APIDocumentTypeDocumentListView.as_view(),
        name='documenttype-document-list'
    ),
    url(
        r'^document_types/(?P<pk>[0-9]+)/$', APIDocumentTypeView.as_view(),
        name='documenttype-detail'
    ),
    url(
        r'^document_types/$', APIDocumentTypeListView.as_view(),
        name='documenttype-list'
    ),
    url(
        r'^trashed_documents/$', APIDeletedDocumentListView.as_view(),
        name='trasheddocument-list'
    ),
    url(
        r'^trashed_documents/(?P<pk>[0-9]+)/$',
        APIDeletedDocumentView.as_view(), name='trasheddocument-detail'
    ),
    url(
        r'^trashed_documents/(?P<pk>[0-9]+)/restore/$',
        APIDeletedDocumentRestoreView.as_view(), name='trasheddocument-restore'
    ),
]
