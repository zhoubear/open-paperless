from __future__ import absolute_import, unicode_literals

from rest_framework import generics
from rest_framework.response import Response

from documents.models import DocumentPage
from rest_api.permissions import MayanPermission

from .models import DocumentPageContent
from .permissions import permission_content_view
from .serializers import DocumentPageContentSerializer


class APIDocumentPageContentView(generics.RetrieveAPIView):
    """
    Returns the content of the selected document page.
    ---
    GET:
        parameters:
            - name: pk
              paramType: path
              type: number
    """

    mayan_object_permissions = {
        'GET': (permission_content_view,),
    }
    permission_classes = (MayanPermission,)
    serializer_class = DocumentPageContentSerializer
    queryset = DocumentPage.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            content = instance.content
        except DocumentPageContent.DoesNotExist:
            content = DocumentPageContent.objects.none()

        serializer = self.get_serializer(content)
        return Response(serializer.data)
