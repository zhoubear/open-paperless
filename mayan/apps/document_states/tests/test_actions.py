from __future__ import unicode_literals

from documents.tests.test_models import GenericDocumentTestCase


class ActionTestCase(GenericDocumentTestCase):
    def setUp(self):
        super(ActionTestCase, self).setUp()

        class MockWorkflowInstance(object):
            document = self.document

        class MockEntryLog(object):
            workflow_instance = MockWorkflowInstance()

        self.entry_log = MockEntryLog()
