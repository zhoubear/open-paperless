from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from acls.models import AccessControlList
from common.generics import (
    SingleObjectCreateView, SingleObjectDeleteView, SingleObjectListView
)
from documents.models import Document

from .models import Comment
from .permissions import (
    permission_comment_create, permission_comment_delete,
    permission_comment_view
)


class DocumentCommentCreateView(SingleObjectCreateView):
    fields = ('comment',)
    model = Comment
    object_verbose_name = _('Comment')

    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_comment_create, user=request.user,
            obj=self.get_document()
        )

        return super(
            DocumentCommentCreateView, self
        ).dispatch(request, *args, **kwargs)

    def get_document(self):
        return get_object_or_404(Document, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'object': self.get_document(),
            'title': _('Add comment to document: %s') % self.get_document(),
        }

    def get_instance_extra_data(self):
        return {
            'document': self.get_document(), 'user': self.request.user,
        }

    def get_save_extra_data(self):
        return {
            '_user': self.request.user,
        }

    def get_post_action_redirect(self):
        return reverse(
            'comments:comments_for_document', args=(self.kwargs['pk'],)
        )


class DocumentCommentDeleteView(SingleObjectDeleteView):
    model = Comment

    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_comment_delete, user=request.user,
            obj=self.get_object().document
        )

        return super(
            DocumentCommentDeleteView, self
        ).dispatch(request, *args, **kwargs)

    def get_delete_extra_data(self):
        return {'_user': self.request.user}

    def get_extra_context(self):
        return {
            'object': self.get_object().document,
            'title': _('Delete comment: %s?') % self.get_object(),
        }

    def get_post_action_redirect(self):
        return reverse(
            'comments:comments_for_document',
            args=(self.get_object().document.pk,)
        )


class DocumentCommentListView(SingleObjectListView):
    def get_document(self):
        return get_object_or_404(Document, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'hide_link': True,
            'hide_object': True,
            'object': self.get_document(),
            'title': _('Comments for document: %s') % self.get_document(),
        }

    def get_object_list(self):
        AccessControlList.objects.check_access(
            permissions=permission_comment_view, user=self.request.user,
            obj=self.get_document()
        )

        return self.get_document().comments.all()
