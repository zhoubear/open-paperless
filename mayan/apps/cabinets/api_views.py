from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.response import Response

from acls.models import AccessControlList
from documents.models import Document
from documents.permissions import permission_document_view
from rest_api.filters import MayanObjectPermissionsFilter
from rest_api.permissions import MayanPermission

from .models import Cabinet
from .permissions import (
    permission_cabinet_add_document, permission_cabinet_create,
    permission_cabinet_delete, permission_cabinet_edit,
    permission_cabinet_remove_document, permission_cabinet_view
)
from .serializers import (
    CabinetDocumentSerializer, CabinetSerializer, NewCabinetDocumentSerializer,
    WritableCabinetSerializer
)


class APIDocumentCabinetListView(generics.ListAPIView):
    """
    Returns a list of all the cabinets to which a document belongs.
    """

    serializer_class = CabinetSerializer

    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_cabinet_view,)}

    def get_queryset(self):
        document = get_object_or_404(Document, pk=self.kwargs['pk'])
        AccessControlList.objects.check_access(
            permissions=permission_document_view, user=self.request.user,
            obj=document
        )

        queryset = document.document_cabinets().all()
        return queryset


class APICabinetListView(generics.ListCreateAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_cabinet_view,)}
    mayan_view_permissions = {'POST': (permission_cabinet_create,)}
    permission_classes = (MayanPermission,)
    queryset = Cabinet.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CabinetSerializer
        elif self.request.method == 'POST':
            return WritableCabinetSerializer

    def get(self, *args, **kwargs):
        """
        Returns a list of all the cabinets.
        """
        return super(APICabinetListView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Create a new cabinet.
        """
        return super(APICabinetListView, self).post(*args, **kwargs)


class APICabinetView(generics.RetrieveUpdateDestroyAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {
        'GET': (permission_cabinet_view,),
        'PUT': (permission_cabinet_edit,),
        'PATCH': (permission_cabinet_edit,),
        'DELETE': (permission_cabinet_delete,)
    }
    permission_classes = (MayanPermission,)
    queryset = Cabinet.objects.all()

    def delete(self, *args, **kwargs):
        """
        Delete the selected cabinet.
        """
        return super(APICabinetView, self).delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Returns the details of the selected cabinet.
        """
        return super(APICabinetView, self).get(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CabinetSerializer
        else:
            return WritableCabinetSerializer

    def patch(self, *args, **kwargs):
        """
        Edit the selected cabinet.
        """
        return super(APICabinetView, self).patch(*args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Edit the selected cabinet.
        """
        return super(APICabinetView, self).put(*args, **kwargs)


class APICabinetDocumentListView(generics.ListCreateAPIView):
    """
    Returns a list of all the documents contained in a particular cabinet.
    """

    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {
        'GET': (permission_cabinet_view,),
        'POST': (permission_cabinet_add_document,)
    }

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CabinetDocumentSerializer
        elif self.request.method == 'POST':
            return NewCabinetDocumentSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'cabinet': self.get_cabinet(),
            'format': self.format_kwarg,
            'request': self.request,
            'view': self
        }

    def get_cabinet(self):
        return get_object_or_404(Cabinet, pk=self.kwargs['pk'])

    def get_queryset(self):
        cabinet = self.get_cabinet()

        return AccessControlList.objects.filter_by_access(
            permission_document_view, self.request.user,
            queryset=cabinet.documents.all()
        )

    def perform_create(self, serializer):
        serializer.save(cabinet=self.get_cabinet())

    def post(self, request, *args, **kwargs):
        """
        Add a document to the selected cabinet.
        """
        return super(APICabinetDocumentListView, self).post(
            request, *args, **kwargs
        )


class APICabinetDocumentView(generics.RetrieveDestroyAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    lookup_url_kwarg = 'document_pk'
    mayan_object_permissions = {
        'GET': (permission_cabinet_view,),
        'DELETE': (permission_cabinet_remove_document,)
    }
    serializer_class = CabinetDocumentSerializer

    def delete(self, request, *args, **kwargs):
        """
        Remove a document from the selected cabinet.
        """

        return super(APICabinetDocumentView, self).delete(
            request, *args, **kwargs
        )

    def get(self, *args, **kwargs):
        """
        Returns the details of the selected cabinet document.
        """

        return super(APICabinetDocumentView, self).get(*args, **kwargs)

    def get_cabinet(self):
        return get_object_or_404(Cabinet, pk=self.kwargs['pk'])

    def get_queryset(self):
        return self.get_cabinet().documents.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'cabinet': self.get_cabinet(),
            'format': self.format_kwarg,
            'request': self.request,
            'view': self
        }

    def perform_destroy(self, instance):
        self.get_cabinet().documents.remove(instance)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        AccessControlList.objects.check_access(
            permissions=permission_document_view, user=self.request.user,
            obj=instance
        )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
