from __future__ import absolute_import, unicode_literals

import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _, ungettext

from acls.models import AccessControlList
from common.views import (
    MultipleObjectFormActionView, MultipleObjectConfirmActionView,
    SingleObjectCreateView, SingleObjectEditView, SingleObjectListView
)
from documents.models import Document
from documents.views import DocumentListView
from documents.permissions import permission_document_view

from .forms import TagMultipleSelectionForm
from .models import Tag
from .permissions import (
    permission_tag_attach, permission_tag_create, permission_tag_delete,
    permission_tag_edit, permission_tag_remove, permission_tag_view
)

logger = logging.getLogger(__name__)


class TagAttachActionView(MultipleObjectFormActionView):
    form_class = TagMultipleSelectionForm
    model = Document
    object_permission = permission_tag_attach
    success_message = _('Tag attach request performed on %(count)d document')
    success_message_plural = _(
        'Tag attach request performed on %(count)d documents'
    )

    def get_extra_context(self):
        queryset = self.get_queryset()

        result = {
            'submit_label': _('Attach'),
            'title': ungettext(
                singular='Attach tags to %(count)d document',
                plural='Attach tags to %(count)d documents',
                number=queryset.count()
            ) % {
                'count': queryset.count(),
            }
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _('Attach tags to document: %s') % queryset.first()
                }
            )

        return result

    def get_form_extra_kwargs(self):
        queryset = self.get_queryset()
        result = {
            'help_text': _('Tags to be attached.'),
            'permission': permission_tag_attach,
            'user': self.request.user
        }

        if queryset.count() == 1:
            result.update(
                {
                    'queryset': Tag.objects.exclude(pk__in=queryset.first().tags.all())
                }
            )

        return result

    def object_action(self, form, instance):
        attached_tags = instance.attached_tags()

        for tag in form.cleaned_data['tags']:
            AccessControlList.objects.check_access(
                obj=tag, permissions=permission_tag_attach,
                user=self.request.user
            )

            if tag in attached_tags:
                messages.warning(
                    self.request, _(
                        'Document "%(document)s" is already tagged as '
                        '"%(tag)s"'
                    ) % {
                        'document': instance, 'tag': tag
                    }
                )
            else:
                tag.attach_to(document=instance, user=self.request.user)
                messages.success(
                    self.request,
                    _(
                        'Tag "%(tag)s" attached successfully to document '
                        '"%(document)s".'
                    ) % {
                        'document': instance, 'tag': tag
                    }
                )


class TagCreateView(SingleObjectCreateView):
    extra_context = {'title': _('Create tag')}
    fields = ('label', 'color')
    model = Tag
    post_action_redirect = reverse_lazy('tags:tag_list')
    view_permission = permission_tag_create


class TagDeleteActionView(MultipleObjectConfirmActionView):
    model = Tag
    post_action_redirect = reverse_lazy('tags:tag_list')
    object_permission = permission_tag_delete
    success_message = _('Tag delete request performed on %(count)d tag')
    success_message_plural = _(
        'Tag delete request performed on %(count)d tags'
    )

    def get_extra_context(self):
        queryset = self.get_queryset()

        result = {
            'message': _('Will be removed from all documents.'),
            'submit_icon': 'fa fa-times',
            'submit_label': _('Delete'),
            'title': ungettext(
                'Delete the selected tag?',
                'Delete the selected tags?',
                queryset.count()
            )
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _('Delete tag: %s') % queryset.first()
                }
            )

        return result

    def object_action(self, instance, form=None):
        try:
            instance.delete()
            messages.success(
                self.request, _('Tag "%s" deleted successfully.') % instance
            )
        except Exception as exception:
            messages.error(
                self.request, _('Error deleting tag "%(tag)s": %(error)s') % {
                    'tag': instance, 'error': exception
                }
            )


class TagEditView(SingleObjectEditView):
    fields = ('label', 'color')
    model = Tag
    object_permission = permission_tag_edit
    post_action_redirect = reverse_lazy('tags:tag_list')

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Edit tag: %s') % self.get_object(),
        }


class TagListView(SingleObjectListView):
    object_permission = permission_tag_view

    def get_extra_context(self):
        return {
            'hide_link': True,
            'title': _('Tags'),
        }

    def get_object_list(self):
        return self.get_tag_queryset()

    def get_tag_queryset(self):
        return Tag.objects.all()


class TagTaggedItemListView(DocumentListView):
    def get_tag(self):
        return get_object_or_404(Tag, pk=self.kwargs['pk'])

    def get_document_queryset(self):
        return self.get_tag().documents.all()

    def get_extra_context(self):
        context = super(TagTaggedItemListView, self).get_extra_context()
        context.update(
            {
                'object': self.get_tag(),
                'title': _('Documents with the tag: %s') % self.get_tag(),
            }
        )
        return context


class DocumentTagListView(TagListView):
    def dispatch(self, request, *args, **kwargs):
        self.document = get_object_or_404(Document, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_document_view, user=request.user,
            obj=self.document
        )

        return super(DocumentTagListView, self).dispatch(
            request, *args, **kwargs
        )

    def get_extra_context(self):
        return {
            'hide_link': True,
            'object': self.document,
            'title': _('Tags for document: %s') % self.document,
        }

    def get_tag_queryset(self):
        return self.document.attached_tags().all()


class TagRemoveActionView(MultipleObjectFormActionView):
    form_class = TagMultipleSelectionForm
    model = Document
    object_permission = permission_tag_remove
    success_message = _('Tag remove request performed on %(count)d document')
    success_message_plural = _(
        'Tag remove request performed on %(count)d documents'
    )

    def get_extra_context(self):
        queryset = self.get_queryset()

        result = {
            'submit_label': _('Remove'),
            'title': ungettext(
                singular='Remove tags to %(count)d document',
                plural='Remove tags to %(count)d documents',
                number=queryset.count()
            ) % {
                'count': queryset.count(),
            }
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _('Remove tags from document: %s') % queryset.first()
                }
            )

        return result

    def get_form_extra_kwargs(self):
        queryset = self.get_queryset()
        result = {
            'help_text': _('Tags to be removed.'),
            'permission': permission_tag_remove,
            'user': self.request.user
        }

        if queryset.count() == 1:
            result.update(
                {
                    'queryset': queryset.first().tags.all()
                }
            )

        return result

    def object_action(self, form, instance):
        attached_tags = instance.attached_tags()

        for tag in form.cleaned_data['tags']:
            AccessControlList.objects.check_access(
                obj=tag, permissions=permission_tag_remove,
                user=self.request.user
            )

            if tag not in attached_tags:
                messages.warning(
                    self.request, _(
                        'Document "%(document)s" wasn\'t tagged as "%(tag)s'
                    ) % {
                        'document': instance, 'tag': tag
                    }
                )
            else:
                tag.remove_from(document=instance, user=self.request.user)
                messages.success(
                    self.request,
                    _(
                        'Tag "%(tag)s" removed successfully from document '
                        '"%(document)s".'
                    ) % {
                        'document': instance, 'tag': tag
                    }
                )
