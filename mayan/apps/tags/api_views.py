from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from acls.models import AccessControlList
from documents.models import Document
from documents.permissions import permission_document_view
from documents.serializers import DocumentSerializer
from rest_api.filters import MayanObjectPermissionsFilter
from rest_api.permissions import MayanPermission

from .models import Tag
from .permissions import (
    permission_tag_attach, permission_tag_create, permission_tag_delete,
    permission_tag_edit, permission_tag_remove, permission_tag_view
)
from .serializers import (
    DocumentTagSerializer, NewDocumentTagSerializer, TagSerializer,
    WritableTagSerializer
)


class APITagListView(generics.ListCreateAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_tag_view,)}
    mayan_view_permissions = {'POST': (permission_tag_create,)}
    permission_classes = (MayanPermission,)
    queryset = Tag.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TagSerializer
        elif self.request.method == 'POST':
            return WritableTagSerializer

    def get(self, *args, **kwargs):
        """
        Returns a list of all the tags.
        """

        return super(APITagListView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Create a new tag.
        """

        return super(APITagListView, self).post(*args, **kwargs)


class APITagView(generics.RetrieveUpdateDestroyAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {
        'DELETE': (permission_tag_delete,),
        'GET': (permission_tag_view,),
        'PATCH': (permission_tag_edit,),
        'PUT': (permission_tag_edit,)
    }
    queryset = Tag.objects.all()

    def delete(self, *args, **kwargs):
        """
        Delete the selected tag.
        """

        return super(APITagView, self).delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Return the details of the selected tag.
        """

        return super(APITagView, self).get(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TagSerializer
        else:
            return WritableTagSerializer

    def patch(self, *args, **kwargs):
        """
        Edit the selected tag.
        """

        return super(APITagView, self).patch(*args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Edit the selected tag.
        """

        return super(APITagView, self).put(*args, **kwargs)


class APITagDocumentListView(generics.ListAPIView):
    """
    Returns a list of all the documents tagged by a particular tag.
    """

    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_document_view,)}
    serializer_class = DocumentSerializer

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_tag_view, user=self.request.user, obj=tag
        )

        return tag.documents.all()


class APIDocumentTagListView(generics.ListCreateAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {
        'GET': (permission_tag_view,),
        'POST': (permission_tag_attach,)
    }

    def get(self, *args, **kwargs):
        """
        Returns a list of all the tags attached to a document.
        """

        return super(APIDocumentTagListView, self).get(*args, **kwargs)

    def get_document(self):
        return get_object_or_404(Document, pk=self.kwargs['document_pk'])

    def get_queryset(self):
        document = self.get_document()

        AccessControlList.objects.check_access(
            permissions=permission_document_view, user=self.request.user,
            obj=document
        )

        return document.attached_tags().all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DocumentTagSerializer
        elif self.request.method == 'POST':
            return NewDocumentTagSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'format': self.format_kwarg,
            'request': self.request,
            'document': self.get_document(),
            'view': self
        }

    def perform_create(self, serializer):
        serializer.save(document=self.get_document())

    def post(self, request, *args, **kwargs):
        """
        Attach a tag to a document.
        """

        return super(
            APIDocumentTagListView, self
        ).post(request, *args, **kwargs)


class APIDocumentTagView(generics.RetrieveDestroyAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {
        'GET': (permission_tag_view,),
        'DELETE': (permission_tag_remove,)
    }
    serializer_class = DocumentTagSerializer

    def delete(self, request, *args, **kwargs):
        """
        Remove a tag from the selected document.
        """

        return super(
            APIDocumentTagView, self
        ).delete(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Returns the details of the selected document tag.
        """

        return super(APIDocumentTagView, self).get(*args, **kwargs)

    def get_document(self):
        document = get_object_or_404(Document, pk=self.kwargs['document_pk'])

        AccessControlList.objects.check_access(
            permissions=permission_document_view, user=self.request.user,
            obj=document
        )
        return document

    def get_queryset(self):
        return self.get_document().attached_tags().all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'format': self.format_kwarg,
            'request': self.request,
            'document': self.get_document(),
            'view': self
        }

    def perform_destroy(self, instance):
        try:
            instance.documents.remove(self.get_document())
        except Exception as exception:
            raise ValidationError(exception)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
