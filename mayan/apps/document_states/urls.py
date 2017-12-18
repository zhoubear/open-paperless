from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIDocumentTypeWorkflowListView, APIWorkflowDocumentTypeList,
    APIWorkflowDocumentTypeView, APIWorkflowInstanceListView,
    APIWorkflowInstanceView, APIWorkflowInstanceLogEntryListView,
    APIWorkflowListView, APIWorkflowStateListView, APIWorkflowStateView,
    APIWorkflowTransitionListView, APIWorkflowTransitionView, APIWorkflowView
)
from .views import (
    DocumentWorkflowInstanceListView, SetupWorkflowCreateView,
    SetupWorkflowDeleteView, SetupWorkflowDocumentTypesView,
    SetupWorkflowEditView, SetupWorkflowListView,
    SetupWorkflowStateActionCreateView, SetupWorkflowStateActionDeleteView,
    SetupWorkflowStateActionEditView, SetupWorkflowStateActionListView,
    SetupWorkflowStateActionSelectionView, SetupWorkflowStateCreateView,
    SetupWorkflowStateDeleteView, SetupWorkflowStateEditView,
    SetupWorkflowStateListView, SetupWorkflowTransitionListView,
    SetupWorkflowTransitionCreateView, SetupWorkflowTransitionDeleteView,
    SetupWorkflowTransitionEditView,
    SetupWorkflowTransitionTriggerEventListView, ToolLaunchAllWorkflows,
    WorkflowDocumentListView, WorkflowInstanceDetailView,
    WorkflowImageView, WorkflowInstanceTransitionView, WorkflowListView,
    WorkflowPreviewView, WorkflowStateDocumentListView, WorkflowStateListView,
)

urlpatterns = [
    url(
        r'^document/(?P<pk>\d+)/workflows/$',
        DocumentWorkflowInstanceListView.as_view(),
        name='document_workflow_instance_list'
    ),
    url(
        r'^document/workflows/(?P<pk>\d+)/$',
        WorkflowInstanceDetailView.as_view(), name='workflow_instance_detail'
    ),
    url(
        r'^document/workflows/(?P<pk>\d+)/transition/$',
        WorkflowInstanceTransitionView.as_view(),
        name='workflow_instance_transition'
    ),
    url(
        r'^setup/all/$', SetupWorkflowListView.as_view(),
        name='setup_workflow_list'
    ),
    url(
        r'^setup/create/$', SetupWorkflowCreateView.as_view(),
        name='setup_workflow_create'
    ),
    url(
        r'^setup/(?P<pk>\d+)/edit/$', SetupWorkflowEditView.as_view(),
        name='setup_workflow_edit'
    ),
    url(
        r'^setup/(?P<pk>\d+)/delete/$', SetupWorkflowDeleteView.as_view(),
        name='setup_workflow_delete'
    ),
    url(
        r'^setup/(?P<pk>\d+)/documents/$',
        WorkflowDocumentListView.as_view(),
        name='setup_workflow_document_list'
    ),
    url(
        r'^setup/(?P<pk>\d+)/document_types/$',
        SetupWorkflowDocumentTypesView.as_view(),
        name='setup_workflow_document_types'
    ),
    url(
        r'^setup/(?P<pk>\d+)/states/$', SetupWorkflowStateListView.as_view(),
        name='setup_workflow_states'
    ),
    url(
        r'^setup/(?P<pk>\d+)/states/create/$',
        SetupWorkflowStateCreateView.as_view(),
        name='setup_workflow_state_create'
    ),
    url(
        r'^setup/(?P<pk>\d+)/transitions/$',
        SetupWorkflowTransitionListView.as_view(),
        name='setup_workflow_transitions'
    ),
    url(
        r'^setup/(?P<pk>\d+)/transitions/create/$',
        SetupWorkflowTransitionCreateView.as_view(),
        name='setup_workflow_transition_create'
    ),
    url(
        r'^setup/(?P<pk>\d+)/transitions/events/$',
        SetupWorkflowTransitionTriggerEventListView.as_view(),
        name='setup_workflow_instance_transition_events'
    ),
    url(
        r'^setup/workflow/state/(?P<pk>\d+)/delete/$',
        SetupWorkflowStateDeleteView.as_view(),
        name='setup_workflow_state_delete'
    ),
    url(
        r'^setup/workflow/state/(?P<pk>\d+)/edit/$',
        SetupWorkflowStateEditView.as_view(),
        name='setup_workflow_state_edit'
    ),
    url(
        r'^setup/workflow/state/(?P<pk>\d+)/actions/$',
        SetupWorkflowStateActionListView.as_view(),
        name='setup_workflow_state_action_list'
    ),
    url(
        r'^setup/workflow/state/(?P<pk>\d+)/actions/$',
        SetupWorkflowStateActionListView.as_view(),
        name='setup_workflow_state_action_list'
    ),
    url(
        r'^setup/workflow/state/(?P<pk>\d+)/actions/selection/$',
        SetupWorkflowStateActionSelectionView.as_view(),
        name='setup_workflow_state_action_selection'
    ),
    url(
        r'^setup/workflow/state/(?P<pk>\d+)/actions/(?P<class_path>[a-zA-Z0-9_.]+)/create/$',
        SetupWorkflowStateActionCreateView.as_view(),
        name='setup_workflow_state_action_create'
    ),

    url(
        r'^setup/workflow/state/actions/(?P<pk>\d+)/delete/$',
        SetupWorkflowStateActionDeleteView.as_view(),
        name='setup_workflow_state_action_delete'
    ),
    url(
        r'^setup/workflow/state/actions/(?P<pk>\d+)/edit/$',
        SetupWorkflowStateActionEditView.as_view(),
        name='setup_workflow_state_action_edit'
    ),


    url(
        r'^setup/workflow/transitions/(?P<pk>\d+)/delete/$',
        SetupWorkflowTransitionDeleteView.as_view(),
        name='setup_workflow_transition_delete'
    ),
    url(
        r'^setup/workflow/transitions/(?P<pk>\d+)/edit/$',
        SetupWorkflowTransitionEditView.as_view(),
        name='setup_workflow_transition_edit'
    ),
    url(
        r'^tools/workflow/all/launch/$',
        ToolLaunchAllWorkflows.as_view(),
        name='tool_launch_all_workflows'
    ),
    url(
        r'all/$',
        WorkflowListView.as_view(),
        name='workflow_list'
    ),
    url(
        r'^(?P<pk>\d+)/documents/$',
        WorkflowDocumentListView.as_view(),
        name='workflow_document_list'
    ),

    url(
        r'^(?P<pk>\d+)/states/$',
        WorkflowStateListView.as_view(),
        name='workflow_state_list'
    ),
    url(
        r'^(?P<pk>\d+)/image/$',
        WorkflowImageView.as_view(),
        name='workflow_image'
    ),
    url(
        r'^(?P<pk>\d+)/preview/$',
        WorkflowPreviewView.as_view(),
        name='workflow_preview'
    ),
    url(
        r'^state/(?P<pk>\d+)/documents/$',
        WorkflowStateDocumentListView.as_view(),
        name='workflow_state_document_list'
    ),
]

api_urls = [
    url(r'^workflows/$', APIWorkflowListView.as_view(), name='workflow-list'),
    url(
        r'^workflows/(?P<pk>[0-9]+)/$', APIWorkflowView.as_view(),
        name='workflow-detail'
    ),
    url(
        r'^workflows/(?P<pk>[0-9]+)/document_types/$',
        APIWorkflowDocumentTypeList.as_view(),
        name='workflow-document-type-list'
    ),
    url(
        r'^workflows/(?P<pk>[0-9]+)/document_types/(?P<document_type_pk>[0-9]+)/$',
        APIWorkflowDocumentTypeView.as_view(),
        name='workflow-document-type-detail'
    ),
    url(
        r'^workflows/(?P<pk>[0-9]+)/states/$',
        APIWorkflowStateListView.as_view(), name='workflowstate-list'
    ),
    url(
        r'^workflows/(?P<pk>[0-9]+)/states/(?P<state_pk>[0-9]+)/$',
        APIWorkflowStateView.as_view(), name='workflowstate-detail'
    ),
    url(
        r'^workflows/(?P<pk>[0-9]+)/transitions/$',
        APIWorkflowTransitionListView.as_view(), name='workflowtransition-list'
    ),
    url(
        r'^workflows/(?P<pk>[0-9]+)/transitions/(?P<transition_pk>[0-9]+)/$',
        APIWorkflowTransitionView.as_view(), name='workflowtransition-detail'
    ),
    url(
        r'^document/(?P<pk>[0-9]+)/workflows/$',
        APIWorkflowInstanceListView.as_view(), name='workflowinstance-list'
    ),
    url(
        r'^document/(?P<pk>[0-9]+)/workflows/(?P<workflow_pk>[0-9]+)/$',
        APIWorkflowInstanceView.as_view(), name='workflowinstance-detail'
    ),
    url(
        r'^document/(?P<pk>[0-9]+)/workflows/(?P<workflow_pk>[0-9]+)/log_entries/$',
        APIWorkflowInstanceLogEntryListView.as_view(),
        name='workflowinstancelogentry-list'
    ),
    url(
        r'^document_type/(?P<pk>[0-9]+)/workflows/$',
        APIDocumentTypeWorkflowListView.as_view(),
        name='documenttype-workflow-list'
    ),
]
