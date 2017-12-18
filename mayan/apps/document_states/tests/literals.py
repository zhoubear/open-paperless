from __future__ import unicode_literals

TEST_INDEX_LABEL = 'test workflow index'

TEST_WORKFLOW_LABEL = 'test workflow label'
TEST_WORKFLOW_INTERNAL_NAME = 'test_workflow_label'
TEST_WORKFLOW_LABEL_EDITED = 'test workflow label edited'
TEST_WORKFLOW_INITIAL_STATE_LABEL = 'test initial state'
TEST_WORKFLOW_INITIAL_STATE_COMPLETION = 33
TEST_WORKFLOW_INSTANCE_LOG_ENTRY_COMMENT = 'test workflow instance log entry comment'
TEST_WORKFLOW_STATE_LABEL = 'test state label'
TEST_WORKFLOW_STATE_LABEL_EDITED = 'test state label edited'
TEST_WORKFLOW_STATE_COMPLETION = 66
TEST_WORKFLOW_TRANSITION_LABEL = 'test transition label'
TEST_WORKFLOW_TRANSITION_LABEL_2 = 'test transition label 2'
TEST_WORKFLOW_TRANSITION_LABEL_EDITED = 'test transition label edited'

TEST_INDEX_TEMPLATE_METADATA_EXPRESSION = '{{{{ document.workflow.{}.get_current_state }}}}'.format(
    TEST_WORKFLOW_INTERNAL_NAME
)
