from __future__ import unicode_literals

from acls.models import AccessControlList
from common.tests.test_views import GenericViewTestCase
from documents.tests.literals import TEST_SMALL_DOCUMENT_PATH
from documents.tests.test_views import GenericDocumentViewTestCase

from ..models import Workflow, WorkflowState, WorkflowTransition
from ..permissions import (
    permission_workflow_tools, permission_workflow_transition
)

from .literals import (
    TEST_WORKFLOW_INITIAL_STATE_LABEL, TEST_WORKFLOW_INITIAL_STATE_COMPLETION,
    TEST_WORKFLOW_INTERNAL_NAME, TEST_WORKFLOW_LABEL,
    TEST_WORKFLOW_STATE_LABEL, TEST_WORKFLOW_STATE_COMPLETION,
    TEST_WORKFLOW_TRANSITION_LABEL, TEST_WORKFLOW_TRANSITION_LABEL_2
)


class DocumentStateViewTestCase(GenericViewTestCase):
    def setUp(self):
        super(DocumentStateViewTestCase, self).setUp()

        self.login_admin_user()

    def _create_workflow(self):
        self.workflow = Workflow.objects.create(
            label=TEST_WORKFLOW_LABEL,
            internal_name=TEST_WORKFLOW_INTERNAL_NAME
        )

    def _create_workflow_states(self):
        self.workflow_initial_state = WorkflowState.objects.create(
            workflow=self.workflow, label=TEST_WORKFLOW_INITIAL_STATE_LABEL,
            completion=TEST_WORKFLOW_INITIAL_STATE_COMPLETION, initial=True
        )
        self.workflow_state = WorkflowState.objects.create(
            workflow=self.workflow, label=TEST_WORKFLOW_STATE_LABEL,
            completion=TEST_WORKFLOW_STATE_COMPLETION
        )

    def _create_workflow_transition(self):
        self.workflow_transition = WorkflowTransition.objects.create(
            workflow=self.workflow, label=TEST_WORKFLOW_TRANSITION_LABEL,
            origin_state=self.workflow_initial_state,
            destination_state=self.workflow_state
        )

    def test_creating_workflow(self):
        response = self.post(
            'document_states:setup_workflow_create',
            data={
                'label': TEST_WORKFLOW_LABEL,
                'internal_name': TEST_WORKFLOW_INTERNAL_NAME,
            }, follow=True
        )

        self.assertEquals(response.status_code, 200)

        self.assertEquals(Workflow.objects.count(), 1)
        self.assertEquals(Workflow.objects.all()[0].label, TEST_WORKFLOW_LABEL)

    def test_delete_workflow(self):
        self._create_workflow()

        response = self.post(
            'document_states:setup_workflow_delete', args=(self.workflow.pk,),
            follow=True
        )

        self.assertEquals(response.status_code, 200)

        self.assertEquals(Workflow.objects.count(), 0)

    def test_create_workflow_state(self):
        self._create_workflow()

        response = self.post(
            'document_states:setup_workflow_state_create',
            args=(self.workflow.pk,),
            data={
                'label': TEST_WORKFLOW_STATE_LABEL,
                'completion': TEST_WORKFLOW_STATE_COMPLETION,
            }, follow=True
        )

        self.assertEquals(response.status_code, 200)

        self.assertEquals(WorkflowState.objects.count(), 1)
        self.assertEquals(
            WorkflowState.objects.all()[0].label, TEST_WORKFLOW_STATE_LABEL
        )
        self.assertEquals(
            WorkflowState.objects.all()[0].completion,
            TEST_WORKFLOW_STATE_COMPLETION
        )

    def test_delete_workflow_state(self):
        self._create_workflow()
        self._create_workflow_states()

        response = self.post(
            'document_states:setup_workflow_state_delete',
            args=(self.workflow_state.pk,), follow=True
        )

        self.assertEquals(response.status_code, 200)

        self.assertEquals(WorkflowState.objects.count(), 1)
        self.assertEquals(Workflow.objects.count(), 1)

    def test_create_workflow_transition(self):
        self._create_workflow()
        self._create_workflow_states()

        response = self.post(
            'document_states:setup_workflow_transition_create',
            args=(self.workflow.pk,), data={
                'label': TEST_WORKFLOW_TRANSITION_LABEL,
                'origin_state': self.workflow_initial_state.pk,
                'destination_state': self.workflow_state.pk,
            }, follow=True
        )

        self.assertEquals(response.status_code, 200)

        self.assertEquals(WorkflowTransition.objects.count(), 1)
        self.assertEquals(
            WorkflowTransition.objects.all()[0].label,
            TEST_WORKFLOW_TRANSITION_LABEL
        )
        self.assertEquals(
            WorkflowTransition.objects.all()[0].origin_state,
            self.workflow_initial_state
        )
        self.assertEquals(
            WorkflowTransition.objects.all()[0].destination_state,
            self.workflow_state
        )

    def test_delete_workflow_transition(self):
        self._create_workflow()
        self._create_workflow_states()
        self._create_workflow_transition()

        response = self.post(
            'document_states:setup_workflow_transition_delete',
            args=(self.workflow_transition.pk,), follow=True
        )

        self.assertEquals(response.status_code, 200)

        self.assertEquals(WorkflowState.objects.count(), 2)
        self.assertEquals(Workflow.objects.count(), 1)
        self.assertEquals(WorkflowTransition.objects.count(), 0)


class DocumentStateToolViewTestCase(GenericDocumentViewTestCase):
    def _create_workflow(self):
        self.workflow = Workflow.objects.create(label=TEST_WORKFLOW_LABEL)
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

    def test_tool_launch_all_workflows_view_no_permission(self):
        self._create_workflow_transition()

        self.login_user()

        self.assertEqual(self.document.workflows.count(), 0)

        response = self.post(
            'document_states:tool_launch_all_workflows',
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.document.workflows.count(), 0)

    def test_tool_launch_all_workflows_view_with_permission(self):
        self._create_workflow_transition()

        self.login_user()
        self.grant_permission(permission=permission_workflow_tools)

        self.assertEqual(self.document.workflows.count(), 0)

        response = self.post(
            'document_states:tool_launch_all_workflows',
        )
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.document.workflows.first().workflow, self.workflow
        )


class DocumentStateTransitionViewTestCase(GenericDocumentViewTestCase):
    def _create_workflow(self):
        self.workflow = Workflow.objects.create(label=TEST_WORKFLOW_LABEL)
        self.workflow.document_types.add(self.document_type)

    def _create_workflow_states(self):
        self.workflow_initial_state = WorkflowState.objects.create(
            workflow=self.workflow, label=TEST_WORKFLOW_INITIAL_STATE_LABEL,
            completion=TEST_WORKFLOW_INITIAL_STATE_COMPLETION, initial=True
        )
        self.workflow_state = WorkflowState.objects.create(
            workflow=self.workflow, label=TEST_WORKFLOW_STATE_LABEL,
            completion=TEST_WORKFLOW_STATE_COMPLETION
        )

    def _create_workflow_transitions(self):
        self.workflow_transition = WorkflowTransition.objects.create(
            workflow=self.workflow, label=TEST_WORKFLOW_TRANSITION_LABEL,
            origin_state=self.workflow_initial_state,
            destination_state=self.workflow_state
        )

        self.workflow_transition_2 = WorkflowTransition.objects.create(
            workflow=self.workflow, label=TEST_WORKFLOW_TRANSITION_LABEL_2,
            origin_state=self.workflow_initial_state,
            destination_state=self.workflow_state
        )

    def _create_document(self):
        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document_2 = self.document_type.new_document(
                file_object=file_object
            )

    def _request_workflow_transition(self, workflow_instance):
        return self.post(
            'document_states:workflow_instance_transition',
            args=(workflow_instance.pk,), data={
                'transition': self.workflow_transition.pk,
            }
        )

    def test_transition_workflow_no_permission(self):
        self.login_user()
        self._create_workflow()
        self._create_workflow_states()
        self._create_workflow_transitions()
        self._create_document()

        workflow_instance = self.document_2.workflows.first()

        response = self._request_workflow_transition(
            workflow_instance=workflow_instance
        )

        self.assertEqual(response.status_code, 200)

        # Workflow should remain in the same initial state
        self.assertEqual(
            workflow_instance.get_current_state(), self.workflow_initial_state
        )

    def test_transition_workflow_with_permission(self):
        """
        Test transitioning a workflow by granting the transition workflow
        permission to the role.
        """

        self.login_user()
        self._create_workflow()
        self._create_workflow_states()
        self._create_workflow_transitions()
        self._create_document()

        workflow_instance = self.document_2.workflows.first()

        self.grant_permission(permission=permission_workflow_transition)
        response = self._request_workflow_transition(
            workflow_instance=workflow_instance
        )

        self.assertEqual(response.status_code, 302)

        # Workflow should remain in the same initial state
        self.assertEqual(
            workflow_instance.get_current_state(), self.workflow_state
        )

    def test_transition_workflow_with_workflow_acl(self):
        """
        Test transitioning a workflow by granting the transition workflow
        permission to the workflow itself via ACL.
        """

        self.login_user()
        self._create_workflow()
        self._create_workflow_states()
        self._create_workflow_transitions()
        self._create_document()

        workflow_instance = self.document_2.workflows.first()

        acl = AccessControlList.objects.create(
            content_object=self.workflow, role=self.role
        )
        acl.permissions.add(permission_workflow_transition.stored_permission)

        response = self._request_workflow_transition(
            workflow_instance=workflow_instance
        )

        self.assertEqual(response.status_code, 302)

        # Workflow should remain in the same initial state
        self.assertEqual(
            workflow_instance.get_current_state(), self.workflow_state
        )

    def test_transition_workflow_with_transition_acl(self):
        """
        Test transitioning a workflow by granting the transition workflow
        permission to the transition via ACL.
        """

        self.login_user()
        self._create_workflow()
        self._create_workflow_states()
        self._create_workflow_transitions()
        self._create_document()

        workflow_instance = self.document_2.workflows.first()

        acl = AccessControlList.objects.create(
            content_object=self.workflow_transition, role=self.role
        )
        acl.permissions.add(permission_workflow_transition.stored_permission)

        response = self._request_workflow_transition(
            workflow_instance=workflow_instance
        )

        self.assertEqual(response.status_code, 302)

        # Workflow should remain in the same initial state
        self.assertEqual(
            workflow_instance.get_current_state(), self.workflow_state
        )
