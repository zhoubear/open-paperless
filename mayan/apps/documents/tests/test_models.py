from __future__ import unicode_literals

from datetime import timedelta
import os
import time

from django.conf import settings
from django.test import override_settings

from common.tests import BaseTestCase

from ..literals import STUB_EXPIRATION_INTERVAL
from ..models import DeletedDocument, Document, DocumentType

from .literals import (
    TEST_DOCUMENT_TYPE_LABEL, TEST_DOCUMENT_PATH, TEST_MULTI_PAGE_TIFF_PATH,
    TEST_PDF_INDIRECT_ROTATE_PATH, TEST_OFFICE_DOCUMENT_PATH,
    TEST_SMALL_DOCUMENT_FILENAME, TEST_SMALL_DOCUMENT_PATH
)


@override_settings(OCR_AUTO_OCR=False)
class GenericDocumentTestCase(BaseTestCase):
    test_document_filename = TEST_SMALL_DOCUMENT_FILENAME

    def setUp(self):
        super(GenericDocumentTestCase, self).setUp()
        self.test_document_path = os.path.join(
            settings.BASE_DIR, 'apps', 'documents', 'tests', 'contrib',
            'sample_documents', self.test_document_filename
        )

        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        with open(self.test_document_path) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object, label=self.test_document_filename
            )

    def tearDown(self):
        self.document_type.delete()
        super(GenericDocumentTestCase, self).tearDown()


@override_settings(OCR_AUTO_OCR=False)
class DocumentTestCase(BaseTestCase):
    def setUp(self):
        super(DocumentTestCase, self).setUp()

        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        with open(TEST_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object, label='mayan_11_1.pdf'
            )

    def tearDown(self):
        self.document_type.delete()
        super(DocumentTestCase, self).tearDown()

    def test_document_creation(self):
        self.assertEqual(self.document_type.label, TEST_DOCUMENT_TYPE_LABEL)

        self.assertEqual(self.document.exists(), True)
        self.assertEqual(self.document.size, 272213)

        self.assertEqual(self.document.file_mimetype, 'application/pdf')
        self.assertEqual(self.document.file_mime_encoding, 'binary')
        self.assertEqual(self.document.label, 'mayan_11_1.pdf')
        self.assertEqual(
            self.document.checksum,
            'c637ffab6b8bb026ed3784afdb07663fddc60099853fae2be93890852a69ecf3'
        )
        self.assertEqual(self.document.page_count, 47)

    def test_version_creation(self):
        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document.new_version(file_object=file_object)

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document.new_version(
                file_object=file_object, comment='test comment 1'
            )

        self.assertEqual(self.document.versions.count(), 3)

    def test_restoring_documents(self):
        self.assertEqual(Document.objects.count(), 1)

        # Trash the document
        self.document.delete()
        self.assertEqual(DeletedDocument.objects.count(), 1)
        self.assertEqual(Document.objects.count(), 0)

        # Restore the document
        self.document.restore()
        self.assertEqual(DeletedDocument.objects.count(), 0)
        self.assertEqual(Document.objects.count(), 1)

    def test_trashing_documents(self):
        self.assertEqual(Document.objects.count(), 1)

        # Trash the document
        self.document.delete()
        self.assertEqual(DeletedDocument.objects.count(), 1)
        self.assertEqual(Document.objects.count(), 0)

        # Delete the document
        self.document.delete()
        self.assertEqual(DeletedDocument.objects.count(), 0)
        self.assertEqual(Document.objects.count(), 0)

    def test_auto_trashing(self):
        """
        Test document type trashing policies. Documents are moved to the
        trash, x amount of time after being uploaded
        """

        self.document_type.trash_time_period = 1
        # 'seconds' is not a choice via the model, used here for convenience
        self.document_type.trash_time_unit = 'seconds'
        self.document_type.save()

        # Needed by MySQL as milliseconds value is not store in timestamp
        # field
        time.sleep(2)

        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(DeletedDocument.objects.count(), 0)

        DocumentType.objects.check_trash_periods()

        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(DeletedDocument.objects.count(), 1)

    def test_auto_delete(self):
        """
        Test document type deletion policies. Documents are deleted from the
        trash, x amount of time after being trashed
        """

        self.document_type.delete_time_period = 1
        # 'seconds' is not a choice via the model, used here for convenience
        self.document_type.delete_time_unit = 'seconds'
        self.document_type.save()

        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(DeletedDocument.objects.count(), 0)

        self.document.delete()

        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(DeletedDocument.objects.count(), 1)

        # Needed by MySQL as milliseconds value is not store in timestamp
        # field
        time.sleep(2)

        DocumentType.objects.check_delete_periods()

        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(DeletedDocument.objects.count(), 0)


@override_settings(OCR_AUTO_OCR=False)
class PDFCompatibilityTestCase(BaseTestCase):
    def test_indirect_rotate(self):
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        with open(TEST_PDF_INDIRECT_ROTATE_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object
            )

        self.assertQuerysetEqual(
            qs=Document.objects.all(), values=(repr(self.document),)
        )


@override_settings(OCR_AUTO_OCR=False)
class OfficeDocumentTestCase(BaseTestCase):
    def setUp(self):
        super(OfficeDocumentTestCase, self).setUp()

        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        with open(TEST_OFFICE_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object
            )

    def tearDown(self):
        self.document_type.delete()
        super(OfficeDocumentTestCase, self).tearDown()

    def test_document_creation(self):
        self.assertEqual(self.document.file_mimetype, 'application/msword')
        self.assertEqual(
            self.document.file_mime_encoding, 'application/mswordbinary'
        )
        self.assertEqual(
            self.document.checksum,
            '03a7e9071d2c6ae05a6588acd7dff1d890fac2772cf61abd470c9ffa6ef71f03'
        )
        self.assertEqual(self.document.page_count, 2)


@override_settings(OCR_AUTO_OCR=False)
class MultiPageTiffTestCase(BaseTestCase):
    def setUp(self):
        super(MultiPageTiffTestCase, self).setUp()
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        with open(TEST_MULTI_PAGE_TIFF_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object
            )

    def tearDown(self):
        self.document_type.delete()
        super(MultiPageTiffTestCase, self).tearDown()

    def test_document_creation(self):
        self.assertEqual(self.document.file_mimetype, 'image/tiff')
        self.assertEqual(self.document.file_mime_encoding, 'binary')
        self.assertEqual(
            self.document.checksum,
            '40adaa9d658b65c70a7f002dfe084a8354bb77c0dfbf1993e31fb024a285fb1d'
        )
        self.assertEqual(self.document.page_count, 2)


class DocumentVersionTestCase(GenericDocumentTestCase):
    def test_add_new_version(self):
        self.assertEqual(self.document.versions.count(), 1)

        with open(TEST_DOCUMENT_PATH) as file_object:
            self.document.new_version(
                file_object=file_object
            )

        self.assertEqual(self.document.versions.count(), 2)

        self.assertEqual(
            self.document.checksum,
            'c637ffab6b8bb026ed3784afdb07663fddc60099853fae2be93890852a69ecf3'
        )

    def test_revert_version(self):
        self.assertEqual(self.document.versions.count(), 1)

        # Needed by MySQL as milliseconds value is not store in timestamp
        # field
        time.sleep(2)

        with open(TEST_DOCUMENT_PATH) as file_object:
            self.document.new_version(
                file_object=file_object
            )

        self.assertEqual(self.document.versions.count(), 2)

        self.document.versions.first().revert()

        self.assertEqual(self.document.versions.count(), 1)


@override_settings(OCR_AUTO_OCR=False)
class DocumentManagerTestCase(BaseTestCase):
    def setUp(self):
        super(DocumentManagerTestCase, self).setUp()
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

    def tearDown(self):
        self.document_type.delete()
        super(DocumentManagerTestCase, self).tearDown()

    def test_document_stubs_deletion(self):
        document_stub = Document.objects.create(
            document_type=self.document_type
        )

        Document.objects.delete_stubs()

        self.assertEqual(Document.objects.count(), 1)

        document_stub.date_added = document_stub.date_added - timedelta(
            seconds=STUB_EXPIRATION_INTERVAL + 1
        )
        document_stub.save()

        Document.objects.delete_stubs()

        self.assertEqual(Document.objects.count(), 0)
