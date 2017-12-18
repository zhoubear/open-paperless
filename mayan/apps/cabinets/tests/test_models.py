from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.test import override_settings

from common.tests import BaseTestCase
from documents.models import DocumentType
from documents.tests import TEST_DOCUMENT_TYPE_LABEL, TEST_SMALL_DOCUMENT_PATH

from ..models import Cabinet

from .literals import TEST_CABINET_LABEL


@override_settings(OCR_AUTO_OCR=False)
class CabinetTestCase(BaseTestCase):
    def setUp(self):
        super(CabinetTestCase, self).setUp()
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object
            )

    def tearDown(self):
        self.document_type.delete()
        super(CabinetTestCase, self).tearDown()

    def test_cabinet_creation(self):
        cabinet = Cabinet.objects.create(label=TEST_CABINET_LABEL)

        self.assertEqual(Cabinet.objects.all().count(), 1)
        self.assertQuerysetEqual(Cabinet.objects.all(), (repr(cabinet),))

    def test_cabinet_duplicate_creation(self):
        cabinet = Cabinet.objects.create(label=TEST_CABINET_LABEL)

        with self.assertRaises(ValidationError):
            cabinet_2 = Cabinet(label=TEST_CABINET_LABEL)
            cabinet_2.validate_unique()
            cabinet_2.save()

        self.assertEqual(Cabinet.objects.all().count(), 1)
        self.assertQuerysetEqual(Cabinet.objects.all(), (repr(cabinet),))

    def test_inner_cabinet_creation(self):
        cabinet = Cabinet.objects.create(label=TEST_CABINET_LABEL)

        inner_cabinet = Cabinet.objects.create(
            parent=cabinet, label=TEST_CABINET_LABEL
        )

        self.assertEqual(Cabinet.objects.all().count(), 2)
        self.assertQuerysetEqual(
            Cabinet.objects.all(), map(repr, (cabinet, inner_cabinet))
        )

    def test_addition_of_documents(self):
        cabinet = Cabinet.objects.create(label=TEST_CABINET_LABEL)
        cabinet.documents.add(self.document)

        self.assertEqual(cabinet.documents.count(), 1)
        self.assertQuerysetEqual(
            cabinet.documents.all(), (repr(self.document),)
        )

    def test_addition_and_deletion_of_documents(self):
        cabinet = Cabinet.objects.create(label=TEST_CABINET_LABEL)
        cabinet.documents.add(self.document)

        self.assertEqual(cabinet.documents.count(), 1)
        self.assertQuerysetEqual(
            cabinet.documents.all(), (repr(self.document),)
        )

        cabinet.documents.remove(self.document)

        self.assertEqual(cabinet.documents.count(), 0)
        self.assertQuerysetEqual(cabinet.documents.all(), ())
