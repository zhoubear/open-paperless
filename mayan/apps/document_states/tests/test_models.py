from __future__ import unicode_literals

from django.test import override_settings

from common.tests import BaseTestCase
from documents.models import DocumentType
from documents.tests import TEST_SMALL_DOCUMENT_PATH, TEST_DOCUMENT_TYPE_LABEL
from document_indexing.models import Index, IndexInstanceNode

from ..models import Workflow

from .literals import (
    TEST_INDEX_LABEL, TEST_INDEX_TEMPLATE_METADATA_EXPRESSION,
    TEST_WORKFLOW_INTERNAL_NAME, TEST_WORKFLOW_INITIAL_STATE_LABEL,
    TEST_WORKFLOW_INITIAL_STATE_COMPLETION, TEST_WORKFLOW_LABEL,
    TEST_WORKFLOW_STATE_LABEL, TEST_WORKFLOW_STATE_COMPLETION,
    TEST_WORKFLOW_TRANSITION_LABEL
)


@override_settings(OCR_AUTO_OCR=False)
class DocumentStateIndexingTestCase(BaseTestCase):
    def tearDown(self):
        self.document_type.delete()
        super(DocumentStateIndexingTestCase, self).tearDown()

    def _create_document_type(self):
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

    def _create_document(self):
        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object
            )

    def _create_workflow(self):
        self.workflow = Workflow.objects.create(
            label=TEST_WORKFLOW_LABEL,
            internal_name=TEST_WORKFLOW_INTERNAL_NAME
        )
        self.workflow.document_types.add(self.document_type)

    def _create_workflow_states(self):
        self._create_workflow()
        self.workflow_state_1 = self.workflow.states.create(
            completion=TEST_WORKFLOW_INITIAL_STATE_COMPLETION,
            initial=True, label=TEST_WORKFLOW_INITIAL_STATE_LABEL
        )
        self.workflow_state_2 = self.workflow.states.create(
            completion=TEST_WORKFLOW_STATE_COMPLETION,
            label=TEST_WORKFLOW_STATE_LABEL
        )

    def _create_workflow_transition(self):
        self._create_workflow_states()
        self.workflow_transition = self.workflow.transitions.create(
            label=TEST_WORKFLOW_TRANSITION_LABEL,
            origin_state=self.workflow_state_1,
            destination_state=self.workflow_state_2,
        )

    def _create_index(self):
        # Create empty index
        index = Index.objects.create(label=TEST_INDEX_LABEL)

        # Add our document type to the new index
        index.document_types.add(self.document_type)

        # Create simple index template
        root = index.template_root
        index.node_templates.create(
            parent=root, expression=TEST_INDEX_TEMPLATE_METADATA_EXPRESSION,
            link_documents=True
        )

    def test_workflow_indexing_initial_state(self):
        self._create_document_type()
        self._create_workflow_transition()
        self._create_index()
        self._create_document()

        self.assertEqual(
            list(
                IndexInstanceNode.objects.values_list('value', flat=True)
            ), ['', TEST_WORKFLOW_INITIAL_STATE_LABEL]
        )

    def test_workflow_indexing_transition(self):
        self._create_document_type()
        self._create_workflow_transition()
        self._create_index()
        self._create_document()

        self.document.workflows.first().do_transition(
            transition=self.workflow_transition,
            user=self.admin_user
        )

        self.assertEqual(
            list(
                IndexInstanceNode.objects.values_list('value', flat=True)
            ), ['', TEST_WORKFLOW_STATE_LABEL]
        )

    def test_workflow_indexing_document_delete(self):
        self._create_document_type()
        self._create_workflow_transition()
        self._create_index()
        self._create_document()

        self.document.workflows.first().do_transition(
            transition=self.workflow_transition,
            user=self.admin_user
        )

        self.document.delete(to_trash=False)

        self.assertEqual(
            list(
                IndexInstanceNode.objects.values_list('value', flat=True)
            ), ['']
        )
