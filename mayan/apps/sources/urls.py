from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIStagingSourceFileView, APIStagingSourceFileImageView,
    APIStagingSourceListView, APIStagingSourceView
)
from .views import (
    SetupSourceCheckView, SetupSourceCreateView, SetupSourceDeleteView,
    SetupSourceEditView, SetupSourceListView, SourceLogListView,
    StagingFileDeleteView, UploadInteractiveVersionView, UploadInteractiveView
)
from .wizards import DocumentCreateWizard

urlpatterns = [
    url(
        r'^staging_file/(?P<pk>\d+)/(?P<encoded_filename>.+)/delete/$',
        StagingFileDeleteView.as_view(), name='staging_file_delete'
    ),

    url(
        r'^upload/document/new/interactive/(?P<source_id>\d+)/$',
        UploadInteractiveView.as_view(), name='upload_interactive'
    ),
    url(
        r'^upload/document/new/interactive/$', UploadInteractiveView.as_view(),
        name='upload_interactive'
    ),

    url(
        r'^upload/document/(?P<document_pk>\d+)/version/interactive/(?P<source_id>\d+)/$',
        UploadInteractiveVersionView.as_view(), name='upload_version'
    ),
    url(
        r'^upload/document/(?P<document_pk>\d+)/version/interactive/$',
        UploadInteractiveVersionView.as_view(), name='upload_version'
    ),

    # Setup views

    url(
        r'^setup/list/$', SetupSourceListView.as_view(),
        name='setup_source_list'
    ),
    url(
        r'^setup/(?P<pk>\d+)/edit/$', SetupSourceEditView.as_view(),
        name='setup_source_edit'
    ),
    url(
        r'^setup/(?P<pk>\d+)/logs/$', SourceLogListView.as_view(),
        name='setup_source_logs'
    ),
    url(
        r'^setup/(?P<pk>\d+)/delete/$', SetupSourceDeleteView.as_view(),
        name='setup_source_delete'
    ),
    url(
        r'^setup/(?P<source_type>\w+)/create/$',
        SetupSourceCreateView.as_view(), name='setup_source_create'
    ),
    url(
        r'^setup/(?P<pk>\d+)/check/$', SetupSourceCheckView.as_view(),
        name='setup_source_check'
    ),

    # Document create views

    url(
        r'^create/from/local/multiple/$', DocumentCreateWizard.as_view(),
        name='document_create_multiple'
    ),
]

api_urls = [
    url(
        r'^staging_folders/file/(?P<staging_folder_pk>[0-9]+)/(?P<encoded_filename>.+)/image/$',
        APIStagingSourceFileImageView.as_view(),
        name='stagingfolderfile-image-view'
    ),
    url(
        r'^staging_folders/file/(?P<staging_folder_pk>[0-9]+)/(?P<encoded_filename>.+)/$',
        APIStagingSourceFileView.as_view(), name='stagingfolderfile-detail'
    ),
    url(
        r'^staging_folders/$', APIStagingSourceListView.as_view(),
        name='stagingfolder-list'
    ),
    url(
        r'^staging_folders/(?P<pk>[0-9]+)/$', APIStagingSourceView.as_view(),
        name='stagingfolder-detail'
    )
]
