from __future__ import unicode_literals

from actstream.models import Action

from documents.tests.test_models import GenericDocumentTestCase

from ..events import (
    event_cabinets_add_document, event_cabinets_remove_document
)
from ..models import Cabinet

from .literals import TEST_CABINET_LABEL


class CabinetsEventsTestCase(GenericDocumentTestCase):
    def setUp(self):
        super(CabinetsEventsTestCase, self).setUp()
        self._create_cabinet()

    def _create_cabinet(self):
        self.cabinet = Cabinet.objects.create(label=TEST_CABINET_LABEL)

    def test_document_cabinet_add_event(self):
        Action.objects.all().delete()
        self.cabinet.add_document(document=self.document)

        self.assertEqual(Action.objects.last().target, self.document)
        self.assertEqual(
            Action.objects.last().verb,
            event_cabinets_add_document.name
        )

    def test_document_cabinet_remove_event(self):
        self.cabinet.add_document(document=self.document)
        Action.objects.all().delete()
        self.cabinet.remove_document(document=self.document)

        self.assertEqual(Action.objects.first().target, self.document)
        self.assertEqual(
            Action.objects.first().verb,
            event_cabinets_remove_document.name
        )
