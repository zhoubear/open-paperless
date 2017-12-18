from __future__ import unicode_literals

from django.core.files.base import File
from django.test import override_settings

from common.tests import BaseTestCase
from documents.models import DocumentType
from documents.tests import TEST_DOCUMENT_PATH, TEST_DOCUMENT_TYPE_LABEL

from ..parsers import PopplerParser


@override_settings(OCR_AUTO_OCR=False)
class ParserTestCase(BaseTestCase):
    def setUp(self):
        super(ParserTestCase, self).setUp()
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        with open(TEST_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=File(file_object)
            )

    def tearDown(self):
        self.document_type.delete()
        super(ParserTestCase, self).tearDown()

    def test_poppler_parser(self):
        parser = PopplerParser()

        parser.process_document_version(self.document.latest_version)

        self.assertTrue(
            'Mayan EDMS Documentation' in self.document.pages.first().content.content
        )
