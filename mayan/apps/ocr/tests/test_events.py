from __future__ import unicode_literals

from actstream.models import Action

from documents.tests.test_models import GenericDocumentTestCase

from ..events import (
    event_ocr_document_version_submit, event_ocr_document_version_finish
)


class OCREventsTestCase(GenericDocumentTestCase):
    def test_document_version_submit_event(self):
        Action.objects.all().delete()
        self.document.submit_for_ocr()

        self.assertEqual(
            Action.objects.last().target, self.document.latest_version
        )
        self.assertEqual(
            Action.objects.last().verb,
            event_ocr_document_version_submit.name
        )

    def test_document_version_finish_event(self):
        Action.objects.all().delete()
        self.document.submit_for_ocr()

        self.assertEqual(
            Action.objects.first().target, self.document.latest_version
        )
        self.assertEqual(
            Action.objects.first().verb,
            event_ocr_document_version_finish.name
        )
