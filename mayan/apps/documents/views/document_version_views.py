from __future__ import absolute_import, unicode_literals

import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from acls.models import AccessControlList
from common.generics import (
    ConfirmView, SingleObjectDetailView, SingleObjectListView
)

from ..events import event_document_view
from ..forms import DocumentVersionDownloadForm, DocumentVersionPreviewForm
from ..models import Document, DocumentVersion
from ..permissions import (
    permission_document_download, permission_document_version_revert,
    permission_document_version_view
)

from .document_views import DocumentDownloadFormView, DocumentDownloadView

logger = logging.getLogger(__name__)


class DocumentVersionListView(SingleObjectListView):
    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_document_version_view, user=request.user,
            obj=self.get_document()
        )

        self.get_document().add_as_recent_document_for_user(request.user)

        return super(
            DocumentVersionListView, self
        ).dispatch(request, *args, **kwargs)

    def get_document(self):
        return get_object_or_404(Document, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'list_as_items': True,
            'object': self.get_document(),
            'title': _('Versions of document: %s') % self.get_document(),
        }

    def get_object_list(self):
        return self.get_document().versions.order_by('-timestamp')


class DocumentVersionRevertView(ConfirmView):
    object_permission = permission_document_version_revert
    object_permission_related = 'document'

    def get_extra_context(self):
        return {
            'message': _(
                'All later version after this one will be deleted too.'
            ),
            'object': self.get_object().document,
            'title': _('Revert to this version?'),
        }

    def get_object(self):
        return get_object_or_404(DocumentVersion, pk=self.kwargs['pk'])

    def view_action(self):
        try:
            self.get_object().revert(_user=self.request.user)
            messages.success(
                self.request, _('Document version reverted successfully')
            )
        except Exception as exception:
            messages.error(
                self.request,
                _('Error reverting document version; %s') % exception
            )


class DocumentVersionDownloadFormView(DocumentDownloadFormView):
    form_class = DocumentVersionDownloadForm
    model = DocumentVersion
    multiple_download_view = None
    querystring_form_fields = (
        'compressed', 'zip_filename', 'preserve_extension'
    )
    single_download_view = 'documents:document_version_download'

    def get_extra_context(self):
        result = super(
            DocumentVersionDownloadFormView, self
        ).get_extra_context()

        result['title'] = _('Download document version')

        return result

    def get_document_queryset(self):
        id_list = self.request.GET.get(
            'id_list', self.request.POST.get('id_list', '')
        )

        if not id_list:
            id_list = self.kwargs['pk']

        return self.model.objects.filter(
            pk__in=id_list.split(',')
        )


class DocumentVersionDownloadView(DocumentDownloadView):
    model = DocumentVersion
    object_permission = permission_document_download

    @staticmethod
    def get_item_file(item):
        return item.file

    def get_encoding(self):
        return self.get_object().encoding

    def get_item_label(self, item):
        preserve_extension = self.request.GET.get(
            'preserve_extension', self.request.POST.get(
                'preserve_extension', False
            )
        )

        preserve_extension = preserve_extension == 'true' or preserve_extension == 'True'

        return item.get_rendered_string(preserve_extension=preserve_extension)

    def get_mimetype(self):
        return self.get_object().mimetype


class DocumentVersionView(SingleObjectDetailView):
    form_class = DocumentVersionPreviewForm
    model = DocumentVersion
    object_permission = permission_document_version_view

    def dispatch(self, request, *args, **kwargs):
        result = super(
            DocumentVersionView, self
        ).dispatch(request, *args, **kwargs)
        self.get_object().document.add_as_recent_document_for_user(
            request.user
        )
        event_document_view.commit(
            actor=request.user, target=self.get_object().document
        )

        return result

    def get_extra_context(self):
        return {
            'hide_labels': True,
            'object': self.get_object(),
            'title': _('Preview of document version: %s') % self.get_object(),
        }
