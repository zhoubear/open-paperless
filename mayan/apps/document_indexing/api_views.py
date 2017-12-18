from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404

from rest_framework import generics

from acls.models import AccessControlList
from documents.models import Document
from documents.permissions import permission_document_view
from documents.serializers import DocumentSerializer
from rest_api.filters import MayanObjectPermissionsFilter
from rest_api.permissions import MayanPermission

from .models import Index, IndexInstanceNode, IndexTemplateNode
from .permissions import (
    permission_document_indexing_create, permission_document_indexing_delete,
    permission_document_indexing_edit, permission_document_indexing_view
)
from .serializers import (
    IndexInstanceNodeSerializer, IndexSerializer, IndexTemplateNodeSerializer
)


class APIIndexListView(generics.ListCreateAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_document_indexing_view,)}
    mayan_view_permissions = {'POST': (permission_document_indexing_create,)}
    queryset = Index.objects.all()
    serializer_class = IndexSerializer

    def get(self, *args, **kwargs):
        """
        Returns a list of all the defined indexes.
        """

        return super(APIIndexListView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Create a new index.
        """

        return super(APIIndexListView, self).post(*args, **kwargs)


class APIIndexView(generics.RetrieveUpdateDestroyAPIView):
    mayan_object_permissions = {
        'GET': (permission_document_indexing_view,),
        'PUT': (permission_document_indexing_edit,),
        'PATCH': (permission_document_indexing_edit,),
        'DELETE': (permission_document_indexing_delete,)
    }
    permission_classes = (MayanPermission,)
    queryset = Index.objects.all()
    serializer_class = IndexSerializer

    def delete(self, *args, **kwargs):
        """
        Delete the selected index.
        """

        return super(APIIndexView, self).delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Returns the details of the selected index.
        """

        return super(APIIndexView, self).get(*args, **kwargs)

    def patch(self, *args, **kwargs):
        """
        Partially edit an index.
        """

        return super(APIIndexView, self).patch(*args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Edit an index.
        """

        return super(APIIndexView, self).put(*args, **kwargs)


class APIIndexNodeInstanceDocumentListView(generics.ListAPIView):
    """
    Returns a list of all the documents contained by a particular index node
    instance.
    """

    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_document_view,)}
    serializer_class = DocumentSerializer

    def get_queryset(self):
        index_node_instance = get_object_or_404(
            IndexInstanceNode, pk=self.kwargs['pk']
        )
        AccessControlList.objects.check_access(
            permissions=permission_document_indexing_view,
            user=self.request.user, obj=index_node_instance.index
        )

        return index_node_instance.documents.all()


class APIIndexTemplateListView(generics.ListAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_document_indexing_view,)}
    serializer_class = IndexTemplateNodeSerializer

    def get(self, *args, **kwargs):
        """
        Returns a list of all the template nodes for the selected index.
        """

        return super(APIIndexTemplateListView, self).get(*args, **kwargs)


class APIIndexTemplateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IndexTemplateNodeSerializer
    queryset = IndexTemplateNode.objects.all()

    permission_classes = (MayanPermission,)
    mayan_object_permissions = {
        'GET': (permission_document_indexing_view,),
        'PUT': (permission_document_indexing_edit,),
        'PATCH': (permission_document_indexing_edit,),
        'DELETE': (permission_document_indexing_edit,)
    }

    def delete(self, *args, **kwargs):
        """
        Delete the selected index template node.
        """

        return super(APIIndexTemplateView, self).delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Returns the details of the selected index template node.
        """

        return super(APIIndexTemplateView, self).get(*args, **kwargs)

    def patch(self, *args, **kwargs):
        """
        Partially edit an index template node.
        """

        return super(APIIndexTemplateView, self).patch(*args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Edit an index template node.
        """

        return super(APIIndexTemplateView, self).put(*args, **kwargs)


class APIDocumentIndexListView(generics.ListAPIView):
    """
    Returns a list of all the indexes to which a document belongs.
    """

    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_document_indexing_view,)}
    serializer_class = IndexInstanceNodeSerializer

    def get_queryset(self):
        document = get_object_or_404(Document, pk=self.kwargs['pk'])
        AccessControlList.objects.check_access(
            permissions=permission_document_view, user=self.request.user,
            obj=document
        )

        return document.index_instance_nodes.all()
