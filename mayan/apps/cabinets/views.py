from __future__ import absolute_import, unicode_literals

import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _, ungettext

from acls.models import AccessControlList
from common.views import (
    MultipleObjectFormActionView, SingleObjectCreateView,
    SingleObjectDeleteView, SingleObjectEditView, SingleObjectListView,
    TemplateView
)
from documents.permissions import permission_document_view
from documents.models import Document

from .forms import CabinetListForm
from .models import Cabinet
from .permissions import (
    permission_cabinet_add_document, permission_cabinet_create,
    permission_cabinet_delete, permission_cabinet_edit,
    permission_cabinet_view, permission_cabinet_remove_document
)
from .widgets import jstree_data

logger = logging.getLogger(__name__)


class CabinetCreateView(SingleObjectCreateView):
    fields = ('label',)
    model = Cabinet
    view_permission = permission_cabinet_create

    def get_extra_context(self):
        return {
            'title': _('Create cabinet'),
        }


class CabinetChildAddView(SingleObjectCreateView):
    fields = ('label',)
    model = Cabinet

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save(commit=False)
        self.object.parent = self.get_object()
        self.object.save()

        return super(CabinetChildAddView, self).form_valid(form)

    def get_object(self, *args, **kwargs):
        cabinet = super(CabinetChildAddView, self).get_object(*args, **kwargs)

        AccessControlList.objects.check_access(
            permissions=permission_cabinet_edit, user=self.request.user,
            obj=cabinet.get_root()
        )

        return cabinet

    def get_extra_context(self):
        return {
            'title': _(
                'Add new level to: %s'
            ) % self.get_object().get_full_path(),
        }


class CabinetDeleteView(SingleObjectDeleteView):
    model = Cabinet
    object_permission = permission_cabinet_delete
    post_action_redirect = reverse_lazy('cabinets:cabinet_list')

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Delete the cabinet: %s?') % self.get_object(),
        }


class CabinetDetailView(TemplateView):
    template_name = 'cabinets/cabinet_details.html'

    def get_document_queryset(self):
        queryset = AccessControlList.objects.filter_by_access(
            permission=permission_document_view, user=self.request.user,
            queryset=self.get_object().documents.all()
        )

        return queryset

    def get_context_data(self, **kwargs):
        data = super(CabinetDetailView, self).get_context_data(**kwargs)

        cabinet = self.get_object()

        data.update(
            {
                'jstree_data': '\n'.join(
                    jstree_data(node=cabinet.get_root(), selected_node=cabinet)
                ),
                'document_list': self.get_document_queryset(),
                'hide_links': True,
                'list_as_items': True,
                'object': cabinet,
                'title': _('Details of cabinet: %s') % cabinet.get_full_path(),
            }
        )

        return data

    def get_object(self):
        cabinet = get_object_or_404(Cabinet, pk=self.kwargs['pk'])

        if cabinet.is_root_node():
            permission_object = cabinet
        else:
            permission_object = cabinet.get_root()

        AccessControlList.objects.check_access(
            permissions=permission_cabinet_view, user=self.request.user,
            obj=permission_object
        )

        return cabinet


class CabinetEditView(SingleObjectEditView):
    fields = ('label',)
    model = Cabinet
    object_permission = permission_cabinet_edit
    post_action_redirect = reverse_lazy('cabinets:cabinet_list')

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Edit cabinet: %s') % self.get_object(),
        }


class CabinetListView(SingleObjectListView):
    object_permission = permission_cabinet_view

    def get_extra_context(self):
        return {
            'hide_link': True,
            'title': _('Cabinets'),
        }

    def get_object_list(self):
        # Add explicit ordering of root nodes since the queryset returned
        # is not affected by the model's order Meta option.
        return Cabinet.objects.root_nodes().order_by('label')


class DocumentCabinetListView(CabinetListView):
    def dispatch(self, request, *args, **kwargs):
        self.document = get_object_or_404(Document, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_document_view, user=request.user,
            obj=self.document
        )

        return super(DocumentCabinetListView, self).dispatch(
            request, *args, **kwargs
        )

    def get_extra_context(self):
        return {
            'hide_link': True,
            'object': self.document,
            'title': _('Cabinets containing document: %s') % self.document,
        }

    def get_object_list(self):
        return self.document.document_cabinets().all()


class DocumentAddToCabinetView(MultipleObjectFormActionView):
    form_class = CabinetListForm
    model = Document
    object_permission = permission_cabinet_add_document
    success_message = _(
        'Add to cabinet request performed on %(count)d document'
    )
    success_message_plural = _(
        'Add to cabinet request performed on %(count)d documents'
    )

    def get_extra_context(self):
        queryset = self.get_queryset()

        result = {
            'submit_label': _('Add'),
            'title': ungettext(
                singular='Add %(count)d document to cabinets',
                plural='Add %(count)d documents to cabinets',
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
                        'Add document "%s" to cabinets'
                    ) % queryset.first()
                }
            )

        return result

    def get_form_extra_kwargs(self):
        queryset = self.get_queryset()
        result = {
            'help_text': _(
                'Cabinets to which the selected documents will be added.'
            ),
            'permission': permission_cabinet_add_document,
            'user': self.request.user
        }

        if queryset.count() == 1:
            result.update(
                {
                    'queryset': Cabinet.objects.exclude(
                        pk__in=queryset.first().cabinets.all()
                    )
                }
            )

        return result

    def object_action(self, form, instance):
        cabinet_membership = instance.cabinets.all()

        for cabinet in form.cleaned_data['cabinets']:
            AccessControlList.objects.check_access(
                obj=cabinet, permissions=permission_cabinet_add_document,
                user=self.request.user
            )
            if cabinet in cabinet_membership:
                messages.warning(
                    self.request, _(
                        'Document: %(document)s is already in '
                        'cabinet: %(cabinet)s.'
                    ) % {
                        'document': instance, 'cabinet': cabinet
                    }
                )
            else:
                cabinet.add_document(
                    document=instance, user=self.request.user
                )
                messages.success(
                    self.request, _(
                        'Document: %(document)s added to cabinet: '
                        '%(cabinet)s successfully.'
                    ) % {
                        'document': instance, 'cabinet': cabinet
                    }
                )


class DocumentRemoveFromCabinetView(MultipleObjectFormActionView):
    form_class = CabinetListForm
    model = Document
    object_permission = permission_cabinet_remove_document
    success_message = _(
        'Remove from cabinet request performed on %(count)d document'
    )
    success_message_plural = _(
        'Remove from cabinet request performed on %(count)d documents'
    )

    def get_extra_context(self):
        queryset = self.get_queryset()

        result = {
            'submit_label': _('Remove'),
            'title': ungettext(
                singular='Remove %(count)d document from cabinets',
                plural='Remove %(count)d documents from cabinets',
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
                        'Remove document "%s" from cabinets'
                    ) % queryset.first()
                }
            )

        return result

    def get_form_extra_kwargs(self):
        queryset = self.get_queryset()
        result = {
            'help_text': _(
                'Cabinets from which the selected documents will be removed.'
            ),
            'permission': permission_cabinet_remove_document,
            'user': self.request.user
        }

        if queryset.count() == 1:
            result.update(
                {
                    'queryset': queryset.first().cabinets.all()
                }
            )

        return result

    def object_action(self, form, instance):
        cabinet_membership = instance.cabinets.all()

        for cabinet in form.cleaned_data['cabinets']:
            AccessControlList.objects.check_access(
                obj=cabinet, permissions=permission_cabinet_remove_document,
                user=self.request.user
            )

            if cabinet not in cabinet_membership:
                messages.warning(
                    self.request, _(
                        'Document: %(document)s is not in cabinet: '
                        '%(cabinet)s.'
                    ) % {
                        'document': instance, 'cabinet': cabinet
                    }
                )
            else:
                cabinet.remove_document(
                    document=instance, user=self.request.user
                )
                messages.success(
                    self.request, _(
                        'Document: %(document)s removed from cabinet: '
                        '%(cabinet)s.'
                    ) % {
                        'document': instance, 'cabinet': cabinet
                    }
                )
