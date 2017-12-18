from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _, ungettext

from common.generics import (
    FormView, MultipleObjectConfirmActionView, SingleObjectDetailView,
    SingleObjectDownloadView, SingleObjectListView
)
from documents.models import Document

from .forms import DocumentContentForm, DocumentTypeSelectForm
from .models import DocumentVersionParseError
from .permissions import permission_content_view, permission_parse_document
from .utils import get_document_content


class DocumentContentView(SingleObjectDetailView):
    form_class = DocumentContentForm
    model = Document
    object_permission = permission_content_view

    def dispatch(self, request, *args, **kwargs):
        result = super(DocumentContentView, self).dispatch(
            request, *args, **kwargs
        )
        self.get_object().add_as_recent_document_for_user(request.user)
        return result

    def get_extra_context(self):
        return {
            'document': self.get_object(),
            'hide_labels': True,
            'object': self.get_object(),
            'title': _('Content for document: %s') % self.get_object(),
        }


class DocumentContentDownloadView(SingleObjectDownloadView):
    model = Document
    object_permission = permission_content_view

    def get_file(self):
        file_object = DocumentContentDownloadView.TextIteratorIO(
            iterator=get_document_content(document=self.get_object())
        )
        return DocumentContentDownloadView.VirtualFile(
            file=file_object, name='{}-content'.format(self.get_object())
        )


class DocumentParsingErrorsListView(SingleObjectListView):
    view_permission = permission_content_view

    def get_document(self):
        return get_object_or_404(Document, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'hide_object': True,
            'object': self.get_document(),
            'title': _(
                'Parsing errors for document: %s'
            ) % self.get_document(),
        }

    def get_object_list(self):
        return self.get_document().latest_version.parsing_errors.all()


class DocumentSubmitView(MultipleObjectConfirmActionView):
    model = Document
    object_permission = permission_parse_document
    success_message = _(
        '%(count)d document added to the parsing queue'
    )
    success_message_plural = _(
        '%(count)d documents added to the parsing queue'
    )

    def get_extra_context(self):
        queryset = self.get_queryset()

        result = {
            'title': ungettext(
                singular='Submit %(count)d document to the parsing queue?',
                plural='Submit %(count)d documents to the parsing queue',
                number=queryset.count()
            ) % {
                'count': queryset.count(),
            }
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _(
                        'Submit document "%s" to the parsing queue'
                    ) % queryset.first()
                }
            )

        return result

    def object_action(self, instance, form=None):
        instance.submit_for_parsing()


class DocumentTypeSubmitView(FormView):
    form_class = DocumentTypeSelectForm
    extra_context = {
        'title': _('Submit all documents of a type for parsing')
    }

    def get_form_extra_kwargs(self):
        return {
            'user': self.request.user
        }

    def get_post_action_redirect(self):
        return reverse('common:tools_list')

    def form_valid(self, form):
        count = 0
        for document in form.cleaned_data['document_type'].documents.all():
            document.submit_for_parsing()
            count += 1

        messages.success(
            self.request, _(
                '%(count)d documents of type "%(document_type)s" added to the '
                'parsing queue.'
            ) % {
                'count': count,
                'document_type': form.cleaned_data['document_type']
            }
        )

        return HttpResponseRedirect(self.get_success_url())


class ParseErrorListView(SingleObjectListView):
    extra_context = {
        'hide_object': True,
        'title': _('Parsing errors'),
    }
    view_permission = permission_content_view

    def get_object_list(self):
        return DocumentVersionParseError.objects.all()
