from __future__ import absolute_import, unicode_literals

from rest_framework import generics, status
from rest_framework.response import Response

from documents.models import Document, DocumentPage, DocumentVersion
from rest_api.permissions import MayanPermission

from .models import DocumentPageOCRContent
from .permissions import permission_ocr_content_view, permission_ocr_document
from .serializers import DocumentPageOCRContentSerializer


class APIDocumentOCRView(generics.GenericAPIView):
    mayan_object_permissions = {
        'POST': (permission_ocr_document,)
    }
    permission_classes = (MayanPermission,)
    queryset = Document.objects.all()

    def get_serializer_class(self):
        return None

    def post(self, request, *args, **kwargs):
        """
        Submit a document for OCR.
        ---
        omit_serializer: true
        parameters:
            - name: pk
              paramType: path
              type: number
        responseMessages:
            - code: 202
              message: Accepted
        """

        self.get_object().submit_for_ocr()
        return Response(status=status.HTTP_202_ACCEPTED)


class APIDocumentVersionOCRView(generics.GenericAPIView):
    mayan_object_permissions = {
        'POST': (permission_ocr_document,)
    }
    permission_classes = (MayanPermission,)
    queryset = DocumentVersion.objects.all()

    def get_serializer_class(self):
        return None

    def post(self, request, *args, **kwargs):
        """
        Submit a document version for OCR.
        ---
        omit_serializer: true
        parameters:
            - name: pk
              paramType: path
              type: number
        responseMessages:
            - code: 202
              message: Accepted
        """

        self.get_object().submit_for_ocr()
        return Response(status=status.HTTP_202_ACCEPTED)


class APIDocumentPageOCRContentView(generics.RetrieveAPIView):
    """
    Returns the OCR content of the selected document page.
    ---
    GET:
        parameters:
            - name: pk
              paramType: path
              type: number
    """

    mayan_object_permissions = {
        'GET': (permission_ocr_content_view,),
    }
    permission_classes = (MayanPermission,)
    serializer_class = DocumentPageOCRContentSerializer
    queryset = DocumentPage.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            ocr_content = instance.ocr_content
        except DocumentPageOCRContent.DoesNotExist:
            ocr_content = DocumentPageOCRContent.objects.none()

        serializer = self.get_serializer(ocr_content)
        return Response(serializer.data)
