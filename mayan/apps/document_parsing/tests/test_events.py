from __future__ import unicode_literals

from actstream.models import Action

from documents.tests.literals import TEST_DOCUMENT_FILENAME
from documents.tests.test_models import GenericDocumentTestCase

from ..events import (
    event_parsing_document_version_submit,
    event_parsing_document_version_finish
)


class DocumentParsingEventsTestCase(GenericDocumentTestCase):
    # Ensure we use a PDF file
    test_document_filename = TEST_DOCUMENT_FILENAME

    def test_document_version_submit_event(self):
        Action.objects.all().delete()
        self.document.submit_for_parsing()

        self.assertEqual(
            Action.objects.last().target, self.document.latest_version
        )
        self.assertEqual(
            Action.objects.last().verb,
            event_parsing_document_version_submit.name
        )

    def test_document_version_finish_event(self):
        Action.objects.all().delete()
        self.document.submit_for_parsing()
        self.assertEqual(
            Action.objects.first().target, self.document.latest_version
        )
        self.assertEqual(
            Action.objects.first().verb,
            event_parsing_document_version_finish.name
        )
