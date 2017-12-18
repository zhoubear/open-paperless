from __future__ import absolute_import, unicode_literals

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from rest_framework import generics

from acls.models import AccessControlList
from documents.models import Document
from permissions import Permission

from .permissions import (
    permission_comment_create, permission_comment_delete,
    permission_comment_view
)
from .serializers import CommentSerializer, WritableCommentSerializer


class APICommentListView(generics.ListCreateAPIView):
    def get(self, *args, **kwargs):
        """
        Returns a list of all the document comments.
        """
        return super(APICommentListView, self).get(*args, **kwargs)

    def get_document(self):
        if self.request.method == 'GET':
            permission_required = permission_comment_view
        else:
            permission_required = permission_comment_create

        document = get_object_or_404(Document, pk=self.kwargs['document_pk'])

        try:
            Permission.check_permissions(
                self.request.user, (permission_required,)
            )
        except PermissionDenied:
            AccessControlList.objects.check_access(
                permission_required, self.request.user, document
            )

        return document

    def get_queryset(self):
        return self.get_document().comments.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CommentSerializer
        else:
            return WritableCommentSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'document': self.get_document(),
            'format': self.format_kwarg,
            'request': self.request,
            'view': self
        }

    def post(self, *args, **kwargs):
        """
        Create a new document comment.
        """
        return super(APICommentListView, self).post(*args, **kwargs)


class APICommentView(generics.RetrieveDestroyAPIView):
    lookup_url_kwarg = 'comment_pk'
    serializer_class = CommentSerializer

    def delete(self, request, *args, **kwargs):
        """
        Delete the selected document comment.
        """

        return super(APICommentView, self).delete(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Returns the details of the selected document comment.
        """

        return super(APICommentView, self).get(*args, **kwargs)

    def get_document(self):
        if self.request.method == 'GET':
            permission_required = permission_comment_view
        else:
            permission_required = permission_comment_delete

        document = get_object_or_404(Document, pk=self.kwargs['document_pk'])

        try:
            Permission.check_permissions(
                self.request.user, (permission_required,)
            )
        except PermissionDenied:
            AccessControlList.objects.check_access(
                permission_required, self.request.user, document
            )

        return document

    def get_queryset(self):
        return self.get_document().comments.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'format': self.format_kwarg,
            'request': self.request,
            'view': self
        }
