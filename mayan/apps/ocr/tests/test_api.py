from __future__ import unicode_literals

import json

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status

from documents.models import DocumentType
from documents.tests import TEST_DOCUMENT_TYPE_LABEL, TEST_SMALL_DOCUMENT_PATH
from rest_api.tests import BaseAPITestCase
from user_management.tests import (
    TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME
)


class OCRAPITestCase(BaseAPITestCase):
    """
    Test the OCR app API endpoints
    """

    def setUp(self):
        super(OCRAPITestCase, self).setUp()

        self.admin_user = get_user_model().objects.create_superuser(
            username=TEST_ADMIN_USERNAME, email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )

        self.client.login(
            username=TEST_ADMIN_USERNAME, password=TEST_ADMIN_PASSWORD
        )

        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object,
            )

    def tearDown(self):
        self.document_type.delete()
        super(OCRAPITestCase, self).tearDown()

    def test_submit_document(self):
        response = self.client.post(
            reverse(
                'rest_api:document-ocr-submit-view',
                args=(self.document.pk,)
            )
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        content = self.document.pages.first().ocr_content.content

        self.assertTrue('Mayan EDMS Documentation' in content)

    def test_submit_document_version(self):
        response = self.client.post(
            reverse(
                'rest_api:document-version-ocr-submit-view',
                args=(self.document.latest_version.pk,)
            )
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        content = self.document.pages.first().ocr_content.content

        self.assertTrue('Mayan EDMS Documentation' in content)

    def test_get_document_version_page_content(self):
        response = self.client.get(
            reverse(
                'rest_api:document-page-content-view',
                args=(self.document.latest_version.pages.first().pk,)
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(
            'Mayan EDMS Documentation' in json.loads(response.content)['content']
        )
