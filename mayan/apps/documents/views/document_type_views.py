from __future__ import absolute_import, unicode_literals

import logging

from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from acls.models import AccessControlList
from common.generics import (
    SingleObjectCreateView, SingleObjectDeleteView, SingleObjectEditView,
    SingleObjectListView
)

from ..forms import DocumentTypeFilenameForm_create
from ..models import DocumentType, DocumentTypeFilename
from ..permissions import (
    permission_document_type_create, permission_document_type_delete,
    permission_document_type_edit, permission_document_type_view
)

from .document_views import DocumentListView

logger = logging.getLogger(__name__)


class DocumentTypeDocumentListView(DocumentListView):
    def get_document_type(self):
        return get_object_or_404(DocumentType, pk=self.kwargs['pk'])

    def get_document_queryset(self):
        return self.get_document_type().documents.all()

    def get_extra_context(self):
        context = super(DocumentTypeDocumentListView, self).get_extra_context()
        context.update(
            {
                'object': self.get_document_type(),
                'title': _('Documents of type: %s') % self.get_document_type()
            }
        )
        return context


class DocumentTypeListView(SingleObjectListView):
    model = DocumentType
    object_permission = permission_document_type_view

    def get_extra_context(self):
        return {
            'hide_link': True,
            'title': _('Document types'),
        }


class DocumentTypeCreateView(SingleObjectCreateView):
    fields = (
        'label', 'trash_time_period', 'trash_time_unit', 'delete_time_period',
        'delete_time_unit'
    )
    model = DocumentType
    post_action_redirect = reverse_lazy('documents:document_type_list')
    view_permission = permission_document_type_create

    def get_extra_context(self):
        return {
            'title': _('Create document type'),
        }


class DocumentTypeDeleteView(SingleObjectDeleteView):
    model = DocumentType
    object_permission = permission_document_type_delete
    post_action_redirect = reverse_lazy('documents:document_type_list')

    def get_extra_context(self):
        return {
            'message': _('All documents of this type will be deleted too.'),
            'object': self.get_object(),
            'title': _('Delete the document type: %s?') % self.get_object(),
        }


class DocumentTypeEditView(SingleObjectEditView):
    fields = (
        'label', 'trash_time_period', 'trash_time_unit', 'delete_time_period',
        'delete_time_unit'
    )
    model = DocumentType
    object_permission = permission_document_type_edit
    post_action_redirect = reverse_lazy('documents:document_type_list')

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Edit document type: %s') % self.get_object(),
        }


class DocumentTypeFilenameCreateView(SingleObjectCreateView):
    form_class = DocumentTypeFilenameForm_create

    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_document_type_edit, user=request.user,
            obj=self.get_document_type()
        )

        return super(DocumentTypeFilenameCreateView, self).dispatch(
            request, *args, **kwargs
        )

    def get_document_type(self):
        return get_object_or_404(DocumentType, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'document_type': self.get_document_type(),
            'navigation_object_list': ('document_type',),
            'title': _(
                'Create quick label for document type: %s'
            ) % self.get_document_type(),
        }

    def get_instance_extra_data(self):
        return {'document_type': self.get_document_type()}


class DocumentTypeFilenameEditView(SingleObjectEditView):
    fields = ('enabled', 'filename',)
    model = DocumentTypeFilename
    object_permission = permission_document_type_edit

    def get_extra_context(self):
        document_type_filename = self.get_object()

        return {
            'document_type': document_type_filename.document_type,
            'filename': document_type_filename,
            'navigation_object_list': ('document_type', 'filename',),
            'title': _(
                'Edit quick label "%(filename)s" from document type '
                '"%(document_type)s"'
            ) % {
                'document_type': document_type_filename.document_type,
                'filename': document_type_filename
            },
        }

    def get_post_action_redirect(self):
        return reverse(
            'documents:document_type_filename_list',
            args=(self.get_object().document_type.pk,)
        )


class DocumentTypeFilenameDeleteView(SingleObjectDeleteView):
    model = DocumentTypeFilename
    object_permission = permission_document_type_edit

    def get_extra_context(self):
        return {
            'document_type': self.get_object().document_type,
            'filename': self.get_object(),
            'navigation_object_list': ('document_type', 'filename',),
            'title': _(
                'Delete the quick label: %(label)s, from document type '
                '"%(document_type)s"?'
            ) % {
                'document_type': self.get_object().document_type,
                'label': self.get_object()
            },
        }

    def get_post_action_redirect(self):
        return reverse(
            'documents:document_type_filename_list',
            args=(self.get_object().document_type.pk,)
        )


class DocumentTypeFilenameListView(SingleObjectListView):
    model = DocumentType
    object_permission = permission_document_type_view

    def get_document_type(self):
        return get_object_or_404(DocumentType, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'document_type': self.get_document_type(),
            'hide_link': True,
            'navigation_object_list': ('document_type',),
            'title': _(
                'Quick labels for document type: %s'
            ) % self.get_document_type(),
        }

    def get_object_list(self):
        return self.get_document_type().filenames.all()
