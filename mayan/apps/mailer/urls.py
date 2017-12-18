from __future__ import unicode_literals

from django.conf.urls import url

from .views import (
    SystemMailerLogEntryListView, MailDocumentLinkView, MailDocumentView,
    UserMailerBackendSelectionView, UserMailingCreateView,
    UserMailingDeleteView, UserMailingEditView, UserMailerLogEntryListView,
    UserMailerTestView, UserMailerListView
)

urlpatterns = [
    url(
        r'^(?P<pk>\d+)/send/link/$', MailDocumentLinkView.as_view(),
        name='send_document_link'
    ),
    url(
        r'^multiple/send/link/$', MailDocumentLinkView.as_view(),
        name='send_multiple_document_link'
    ),
    url(
        r'^(?P<pk>\d+)/send/document/$', MailDocumentView.as_view(),
        name='send_document'
    ),
    url(
        r'^multiple/send/document/$', MailDocumentView.as_view(),
        name='send_multiple_document'
    ),
    url(
        r'^system_mailer/log/$', SystemMailerLogEntryListView.as_view(),
        name='system_mailer_error_log'
    ),
    url(
        r'^user_mailers/backend/selection/$',
        UserMailerBackendSelectionView.as_view(),
        name='user_mailer_backend_selection'
    ),
    url(
        r'^user_mailers/(?P<class_path>[a-zA-Z0-9_.]+)/create/$',
        UserMailingCreateView.as_view(), name='user_mailer_create'
    ),
    url(
        r'^user_mailers/(?P<pk>\d+)/delete/$', UserMailingDeleteView.as_view(),
        name='user_mailer_delete'
    ),
    url(
        r'^user_mailers/(?P<pk>\d+)/edit/$', UserMailingEditView.as_view(),
        name='user_mailer_edit'
    ),
    url(
        r'^user_mailers/(?P<pk>\d+)/log/$',
        UserMailerLogEntryListView.as_view(), name='user_mailer_log'
    ),
    url(
        r'^user_mailers/(?P<pk>\d+)/test/$',
        UserMailerTestView.as_view(), name='user_mailer_test'
    ),
    url(
        r'^user_mailers/$', UserMailerListView.as_view(),
        name='user_mailer_list'
    ),
]
