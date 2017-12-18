# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import override_settings

from common.tests import BaseTestCase
from documents.models import DocumentType
from documents.tests import TEST_SMALL_DOCUMENT_PATH, TEST_DOCUMENT_TYPE_LABEL

from ..models import SmartLink

from .literals import TEST_SMART_LINK_LABEL, TEST_SMART_LINK_DYNAMIC_LABEL


@override_settings(OCR_AUTO_OCR=False)
class SmartLinkTestCase(BaseTestCase):
    def setUp(self):
        super(SmartLinkTestCase, self).setUp()
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object
            )

    def tearDown(self):
        self.document_type.delete()
        super(SmartLinkTestCase, self).tearDown()

    def test_dynamic_label(self):
        smart_link = SmartLink.objects.create(
            label=TEST_SMART_LINK_LABEL,
            dynamic_label=TEST_SMART_LINK_DYNAMIC_LABEL
        )
        smart_link.document_types.add(self.document_type)

        self.assertEqual(
            smart_link.get_dynamic_label(document=self.document),
            self.document.label
        )
