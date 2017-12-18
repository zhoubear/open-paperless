from __future__ import unicode_literals

from django.test import override_settings

from documents.tests.test_views import GenericDocumentViewTestCase

from ..permissions import permission_ocr_content_view
from ..utils import get_document_ocr_content


@override_settings(OCR_AUTO_OCR=True)
class OCRViewsTestCase(GenericDocumentViewTestCase):
    # PyOCR's leak descriptor in get_available_languages and image_to_string
    # Disable descriptor leak test until fixed in upstream
    _skip_file_descriptor_test = True

    def setUp(self):
        super(OCRViewsTestCase, self).setUp()
        self.login_user()

    def _document_content_view(self):
        return self.get(
            'ocr:document_content', args=(self.document.pk,)
        )

    def test_document_content_view_no_permissions(self):
        response = self._document_content_view()

        self.assertEqual(response.status_code, 403)

    def test_document_content_view_with_permission(self):
        self.grant_permission(permission=permission_ocr_content_view)

        response = self._document_content_view()

        self.assertContains(
            response, 'Mayan EDMS Documentation', status_code=200
        )

    def test_document_ocr_download_view_no_permission(self):
        response = self.get(
            'ocr:document_ocr_download', args=(self.document.pk,)
        )

        self.assertEqual(response.status_code, 403)

    def test_document_download_view_with_permission(self):
        self.expected_content_type = 'application/octet-stream; charset=utf-8'

        self.grant_permission(permission=permission_ocr_content_view)
        response = self.get(
            'ocr:document_ocr_download', args=(self.document.pk,)
        )

        self.assertEqual(response.status_code, 200)

        self.assert_download_response(
            response, content=(
                ''.join(get_document_ocr_content(document=self.document))
            ),
        )
