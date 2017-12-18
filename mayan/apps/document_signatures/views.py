from __future__ import absolute_import, unicode_literals

import logging

from django.contrib import messages
from django.core.files import File
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from acls.models import AccessControlList
from common.generics import (
    ConfirmView, FormView, SingleObjectCreateView, SingleObjectDeleteView,
    SingleObjectDetailView, SingleObjectDownloadView, SingleObjectListView
)
from common.utils import TemporaryFile
from django_gpg.exceptions import NeedPassphrase, PassphraseError
from django_gpg.permissions import permission_key_sign
from documents.models import DocumentVersion

from .forms import (
    DocumentVersionSignatureCreateForm,
    DocumentVersionSignatureDetailForm
)
from .models import DetachedSignature, SignatureBaseModel
from .permissions import (
    permission_document_version_sign_detached,
    permission_document_version_sign_embedded,
    permission_document_version_signature_delete,
    permission_document_version_signature_download,
    permission_document_version_signature_upload,
    permission_document_version_signature_verify,
    permission_document_version_signature_view,
)
from .tasks import task_verify_missing_embedded_signature

logger = logging.getLogger(__name__)


class DocumentVersionDetachedSignatureCreateView(FormView):
    form_class = DocumentVersionSignatureCreateForm

    def form_valid(self, form):
        key = form.cleaned_data['key']
        passphrase = form.cleaned_data['passphrase'] or None

        AccessControlList.objects.check_access(
            permissions=permission_key_sign, user=self.request.user, obj=key
        )

        try:
            with self.get_document_version().open() as file_object:
                detached_signature = key.sign_file(
                    file_object=file_object, detached=True,
                    passphrase=passphrase
                )
        except NeedPassphrase:
            messages.error(
                self.request, _('Passphrase is needed to unlock this key.')
            )
            return HttpResponseRedirect(
                reverse(
                    'signatures:document_version_signature_detached_create',
                    args=(self.get_document_version().pk,)
                )
            )
        except PassphraseError:
            messages.error(
                self.request, _('Passphrase is incorrect.')
            )
            return HttpResponseRedirect(
                reverse(
                    'signatures:document_version_signature_detached_create',
                    args=(self.get_document_version().pk,)
                )
            )
        else:
            temporary_file_object = TemporaryFile()
            temporary_file_object.write(detached_signature.data)
            temporary_file_object.seek(0)

            DetachedSignature.objects.create(
                document_version=self.get_document_version(),
                signature_file=File(temporary_file_object)
            )

            temporary_file_object.close()

            messages.success(
                self.request, _('Document version signed successfully.')
            )

        return super(
            DocumentVersionDetachedSignatureCreateView, self
        ).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_document_version_sign_detached,
            user=request.user, obj=self.get_document_version().document
        )

        return super(
            DocumentVersionDetachedSignatureCreateView, self
        ).dispatch(request, *args, **kwargs)

    def get_document_version(self):
        return get_object_or_404(DocumentVersion, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'object': self.get_document_version(),
            'title': _(
                'Sign document version "%s" with a detached signature'
            ) % self.get_document_version(),
        }

    def get_form_kwargs(self):
        result = super(
            DocumentVersionDetachedSignatureCreateView, self
        ).get_form_kwargs()

        result.update({'user': self.request.user})

        return result

    def get_post_action_redirect(self):
        return reverse(
            'signatures:document_version_signature_list',
            args=(self.get_document_version().pk,)
        )


class DocumentVersionEmbeddedSignatureCreateView(FormView):
    form_class = DocumentVersionSignatureCreateForm

    def form_valid(self, form):
        key = form.cleaned_data['key']
        passphrase = form.cleaned_data['passphrase'] or None

        AccessControlList.objects.check_access(
            permissions=permission_key_sign, user=self.request.user, obj=key
        )

        try:
            with self.get_document_version().open() as file_object:
                signature_result = key.sign_file(
                    binary=True, file_object=file_object, passphrase=passphrase
                )
        except NeedPassphrase:
            messages.error(
                self.request, _('Passphrase is needed to unlock this key.')
            )
            return HttpResponseRedirect(
                reverse(
                    'signatures:document_version_signature_embedded_create',
                    args=(self.get_document_version().pk,)
                )
            )
        except PassphraseError:
            messages.error(
                self.request, _('Passphrase is incorrect.')
            )
            return HttpResponseRedirect(
                reverse(
                    'signatures:document_version_signature_embedded_create',
                    args=(self.get_document_version().pk,)
                )
            )
        else:
            temporary_file_object = TemporaryFile()
            temporary_file_object.write(signature_result.data)
            temporary_file_object.seek(0)

            new_version = self.get_document_version().document.new_version(
                file_object=temporary_file_object, _user=self.request.user
            )

            temporary_file_object.close()

            messages.success(
                self.request, _('Document version signed successfully.')
            )

            return HttpResponseRedirect(
                reverse(
                    'signatures:document_version_signature_list',
                    args=(new_version.pk,)
                )
            )

        return super(
            DocumentVersionEmbeddedSignatureCreateView, self
        ).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_document_version_sign_embedded,
            user=request.user, obj=self.get_document_version().document
        )

        return super(
            DocumentVersionEmbeddedSignatureCreateView, self
        ).dispatch(request, *args, **kwargs)

    def get_document_version(self):
        return get_object_or_404(DocumentVersion, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'object': self.get_document_version(),
            'title': _(
                'Sign document version "%s" with a embedded signature'
            ) % self.get_document_version(),
        }

    def get_form_kwargs(self):
        result = super(
            DocumentVersionEmbeddedSignatureCreateView, self
        ).get_form_kwargs()

        result.update({'user': self.request.user})

        return result


class DocumentVersionSignatureDeleteView(SingleObjectDeleteView):
    model = DetachedSignature
    object_permission = permission_document_version_signature_delete
    object_permission_related = 'document_version.document'

    def get_extra_context(self):
        return {
            'object': self.get_object().document_version,
            'signature': self.get_object(),
            'title': _('Delete detached signature: %s') % self.get_object()
        }

    def get_post_action_redirect(self):
        return reverse(
            'signatures:document_version_signature_list',
            args=(self.get_object().document_version.pk,)
        )


class DocumentVersionSignatureDetailView(SingleObjectDetailView):
    form_class = DocumentVersionSignatureDetailForm
    object_permission = permission_document_version_signature_view
    object_permission_related = 'document_version.document'

    def get_extra_context(self):
        return {
            'hide_object': True,
            'object': self.get_object().document_version,
            'signature': self.get_object(),
            'title': _(
                'Details for signature: %s'
            ) % self.get_object(),
        }

    def get_queryset(self):
        return SignatureBaseModel.objects.select_subclasses()


class DocumentVersionSignatureDownloadView(SingleObjectDownloadView):
    model = DetachedSignature
    object_permission = permission_document_version_signature_download
    object_permission_related = 'document_version.document'

    def get_file(self):
        signature = self.get_object()

        return DocumentVersionSignatureDownloadView.VirtualFile(
            signature.signature_file, name=force_text(signature)
        )


class DocumentVersionSignatureListView(SingleObjectListView):
    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_document_version_signature_view,
            user=request.user, obj=self.get_document_version()
        )

        return super(
            DocumentVersionSignatureListView, self
        ).dispatch(request, *args, **kwargs)

    def get_document_version(self):
        return get_object_or_404(DocumentVersion, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'hide_object': True,
            'object': self.get_document_version(),
            'title': _(
                'Signatures for document version: %s'
            ) % self.get_document_version(),
        }

    def get_object_list(self):
        return self.get_document_version().signatures.all()


class DocumentVersionSignatureUploadView(SingleObjectCreateView):
    fields = ('signature_file',)
    model = DetachedSignature

    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_document_version_signature_upload,
            user=request.user, obj=self.get_document_version()
        )

        return super(
            DocumentVersionSignatureUploadView, self
        ).dispatch(request, *args, **kwargs)

    def get_document_version(self):
        return get_object_or_404(DocumentVersion, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'object': self.get_document_version(),
            'title': _(
                'Upload detached signature for document version: %s'
            ) % self.get_document_version(),
        }

    def get_instance_extra_data(self):
        return {'document_version': self.get_document_version()}

    def get_post_action_redirect(self):
        return reverse(
            'signatures:document_version_signature_list',
            args=(self.get_document_version().pk,)
        )


class AllDocumentSignatureVerifyView(ConfirmView):
    extra_context = {
        'message': _(
            'On large databases this operation may take some time to execute.'
        ), 'title': _('Verify all document for signatures?'),
    }
    view_permission = permission_document_version_signature_verify

    def get_post_action_redirect(self):
        return reverse('common:tools_list')

    def view_action(self):
        task_verify_missing_embedded_signature.delay()
        messages.success(
            self.request, _('Signature verification queued successfully.')
        )
