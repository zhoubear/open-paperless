from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404

from rest_framework import generics

from acls.models import AccessControlList
from documents.models import Document, DocumentType
from documents.permissions import (
    permission_document_type_view, permission_document_type_edit
)
from rest_api.filters import MayanObjectPermissionsFilter
from rest_api.permissions import MayanPermission

from .models import MetadataType
from .permissions import (
    permission_metadata_document_add, permission_metadata_document_remove,
    permission_metadata_document_edit, permission_metadata_document_view,
    permission_metadata_type_create, permission_metadata_type_delete,
    permission_metadata_type_edit, permission_metadata_type_view
)
from .serializers import (
    DocumentMetadataSerializer, DocumentTypeMetadataTypeSerializer,
    MetadataTypeSerializer, NewDocumentMetadataSerializer,
    NewDocumentTypeMetadataTypeSerializer,
    WritableDocumentTypeMetadataTypeSerializer
)


class APIDocumentMetadataListView(generics.ListCreateAPIView):
    def get(self, *args, **kwargs):
        """
        Returns a list of selected document's metadata types and values.
        """

        return super(APIDocumentMetadataListView, self).get(*args, **kwargs)

    def get_document(self):
        if self.request.method == 'GET':
            permission_required = permission_metadata_document_view
        else:
            permission_required = permission_metadata_document_add

        document = get_object_or_404(
            Document, pk=self.kwargs['document_pk']
        )

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=document
        )

        return document

    def get_queryset(self):
        return self.get_document().metadata.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DocumentMetadataSerializer
        else:
            return NewDocumentMetadataSerializer

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
        Add an existing metadata type and value to the selected document.
        """

        return super(APIDocumentMetadataListView, self).post(*args, **kwargs)


class APIDocumentMetadataView(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = 'metadata_pk'

    def delete(self, *args, **kwargs):
        """
        Remove this metadata entry from the selected document.
        """

        return super(APIDocumentMetadataView, self).delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Return the details of the selected document metadata type and value.
        """

        return super(APIDocumentMetadataView, self).get(*args, **kwargs)

    def get_document(self):
        if self.request.method == 'GET':
            permission_required = permission_metadata_document_view
        elif self.request.method == 'PUT':
            permission_required = permission_metadata_document_edit
        elif self.request.method == 'PATCH':
            permission_required = permission_metadata_document_edit
        elif self.request.method == 'DELETE':
            permission_required = permission_metadata_document_remove

        document = get_object_or_404(
            Document, pk=self.kwargs['document_pk']
        )

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=document
        )

        return document

    def get_queryset(self):
        return self.get_document().metadata.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DocumentMetadataSerializer
        else:
            return DocumentMetadataSerializer

    def patch(self, *args, **kwargs):
        """
        Edit the selected document metadata type and value.
        """

        return super(APIDocumentMetadataView, self).patch(*args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Edit the selected document metadata type and value.
        """

        return super(APIDocumentMetadataView, self).put(*args, **kwargs)


class APIMetadataTypeListView(generics.ListCreateAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_metadata_type_view,)}
    mayan_view_permissions = {'POST': (permission_metadata_type_create,)}
    permission_classes = (MayanPermission,)
    queryset = MetadataType.objects.all()
    serializer_class = MetadataTypeSerializer

    def get(self, *args, **kwargs):
        """
        Returns a list of all the metadata types.
        """

        return super(APIMetadataTypeListView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Create a new metadata type.
        """

        return super(APIMetadataTypeListView, self).post(*args, **kwargs)


class APIMetadataTypeView(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = 'metadata_type_pk'
    mayan_object_permissions = {
        'GET': (permission_metadata_type_view,),
        'PUT': (permission_metadata_type_edit,),
        'PATCH': (permission_metadata_type_edit,),
        'DELETE': (permission_metadata_type_delete,)
    }
    permission_classes = (MayanPermission,)
    queryset = MetadataType.objects.all()
    serializer_class = MetadataTypeSerializer

    def delete(self, *args, **kwargs):
        """
        Delete the selected metadata type.
        """

        return super(APIMetadataTypeView, self).delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Return the details of the selected metadata type.
        """

        return super(APIMetadataTypeView, self).get(*args, **kwargs)

    def patch(self, *args, **kwargs):
        """
        Edit the selected metadata type.
        """

        return super(APIMetadataTypeView, self).patch(*args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Edit the selected metadata type.
        """

        return super(APIMetadataTypeView, self).put(*args, **kwargs)


class APIDocumentTypeMetadataTypeListView(generics.ListCreateAPIView):
    lookup_url_kwarg = 'metadata_type_pk'

    def get(self, *args, **kwargs):
        """
        Returns a list of selected document type's metadata types.
        """

        return super(
            APIDocumentTypeMetadataTypeListView, self
        ).get(*args, **kwargs)

    def get_document_type(self):
        if self.request.method == 'GET':
            permission_required = permission_document_type_view
        else:
            permission_required = permission_document_type_edit

        document_type = get_object_or_404(
            DocumentType, pk=self.kwargs['document_type_pk']
        )

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=document_type
        )

        return document_type

    def get_queryset(self):
        return self.get_document_type().metadata.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DocumentTypeMetadataTypeSerializer
        else:
            return NewDocumentTypeMetadataTypeSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """

        return {
            'document_type': self.get_document_type(),
            'format': self.format_kwarg,
            'request': self.request,
            'view': self
        }

    def post(self, *args, **kwargs):
        """
        Add a metadata type to the selected document type.
        """

        return super(
            APIDocumentTypeMetadataTypeListView, self
        ).post(*args, **kwargs)


class APIDocumentTypeMetadataTypeView(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = 'metadata_type_pk'
    serializer_class = DocumentTypeMetadataTypeSerializer

    def delete(self, *args, **kwargs):
        """
        Remove a metadata type from a document type.
        """

        return super(
            APIDocumentTypeMetadataTypeView, self
        ).delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Retrieve the details of a document type metadata type.
        """

        return super(
            APIDocumentTypeMetadataTypeView, self
        ).get(*args, **kwargs)

    def get_document_type(self):
        if self.request.method == 'GET':
            permission_required = permission_document_type_view
        else:
            permission_required = permission_document_type_edit

        document_type = get_object_or_404(
            DocumentType, pk=self.kwargs['document_type_pk']
        )

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=document_type
        )

        return document_type

    def get_queryset(self):
        return self.get_document_type().metadata.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DocumentTypeMetadataTypeSerializer
        else:
            return WritableDocumentTypeMetadataTypeSerializer

    def patch(self, *args, **kwargs):
        """
        Edit the selected document type metadata type.
        """

        return super(
            APIDocumentTypeMetadataTypeView, self
        ).patch(*args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Edit the selected document type metadata type.
        """

        return super(
            APIDocumentTypeMetadataTypeView, self
        ).put(*args, **kwargs)
