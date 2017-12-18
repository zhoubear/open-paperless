from __future__ import unicode_literals

from django.apps import apps
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from kombu import Exchange, Queue

from acls import ModelPermission
from acls.links import link_acl_list
from common import (
    MayanAppConfig, menu_facet, menu_main, menu_object, menu_secondary,
    menu_setup, menu_sidebar, menu_tools
)
from common.classes import ModelAttribute
from common.links import link_object_error_list
from common.permissions_runtime import permission_error_log_view
from common.widgets import two_state_template
from mayan.celery import app
from navigation import SourceColumn
from rest_api.classes import APIEndPoint

from .classes import DocumentStateHelper, WorkflowAction
from .handlers import (
    handler_index_document, handler_trigger_transition, launch_workflow
)
from .links import (
    link_document_workflow_instance_list, link_setup_workflow_document_types,
    link_setup_workflow_create, link_setup_workflow_delete,
    link_setup_workflow_edit, link_setup_workflow_list,
    link_setup_workflow_states, link_setup_workflow_state_action_delete,
    link_setup_workflow_state_action_edit,
    link_setup_workflow_state_action_list,
    link_setup_workflow_state_action_selection,
    link_setup_workflow_state_create, link_setup_workflow_state_delete,
    link_setup_workflow_state_edit, link_setup_workflow_transitions,
    link_setup_workflow_transition_create,
    link_setup_workflow_transition_delete, link_setup_workflow_transition_edit,
    link_tool_launch_all_workflows, link_workflow_instance_detail,
    link_workflow_instance_transition, link_workflow_document_list,
    link_workflow_list, link_workflow_preview,
    link_workflow_state_document_list, link_workflow_state_list,
    link_workflow_instance_transition_events
)
from .permissions import (
    permission_workflow_delete, permission_workflow_edit,
    permission_workflow_transition, permission_workflow_view
)
from .queues import *  # NOQA
from .widgets import widget_transition_events


class DocumentStatesApp(MayanAppConfig):
    app_url = 'states'
    has_tests = True
    name = 'document_states'
    verbose_name = _('Document states')

    def ready(self):
        super(DocumentStatesApp, self).ready()

        APIEndPoint(app=self, version_string='1')

        Action = apps.get_model(
            app_label='actstream', model_name='Action'
        )
        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )
        ErrorLogEntry = apps.get_model(
            app_label='common', model_name='ErrorLogEntry'
        )

        Workflow = self.get_model('Workflow')
        WorkflowInstance = self.get_model('WorkflowInstance')
        WorkflowInstanceLogEntry = self.get_model('WorkflowInstanceLogEntry')
        WorkflowRuntimeProxy = self.get_model('WorkflowRuntimeProxy')
        WorkflowState = self.get_model('WorkflowState')
        WorkflowStateAction = self.get_model('WorkflowStateAction')
        WorkflowStateRuntimeProxy = self.get_model('WorkflowStateRuntimeProxy')
        WorkflowTransition = self.get_model('WorkflowTransition')
        WorkflowTransitionTriggerEvent = self.get_model(
            'WorkflowTransitionTriggerEvent'
        )

        Document.add_to_class(
            'workflow', DocumentStateHelper.constructor
        )

        ErrorLogEntry.objects.register(model=WorkflowStateAction)

        WorkflowAction.initialize()

        ModelAttribute(
            Document, 'workflow.< workflow internal name >.get_current_state',
            label=_('Current state of a workflow'), description=_(
                'Return the current state of the selected workflow'
            ), type_name=['property', 'indexing']
        )
        ModelAttribute(
            Document,
            'workflow.< workflow internal name >.get_current_state.completion',
            label=_('Current state of a workflow'), description=_(
                'Return the completion value of the current state of the '
                'selected workflow'
            ), type_name=['property', 'indexing']
        )

        ModelPermission.register(
            model=Workflow, permissions=(
                permission_error_log_view, permission_workflow_delete,
                permission_workflow_edit, permission_workflow_transition,
                permission_workflow_view,
            )
        )

        ModelPermission.register_inheritance(
            model=WorkflowInstance, related='workflow',
        )
        ModelPermission.register_inheritance(
            model=WorkflowInstanceLogEntry,
            related='workflow_instance__workflow',
        )
        ModelPermission.register(
            model=WorkflowTransition,
            permissions=(permission_workflow_transition,)
        )

        ModelPermission.register_inheritance(
            model=WorkflowState, related='workflow',
        )
        ModelPermission.register_inheritance(
            model=WorkflowStateAction, related='state__workflow',
        )
        ModelPermission.register_inheritance(
            model=WorkflowTransition, related='workflow',
        )
        ModelPermission.register_inheritance(
            model=WorkflowTransitionTriggerEvent,
            related='transition__workflow',
        )

        SourceColumn(
            source=Workflow, label=_('Label'), attribute='label'
        )
        SourceColumn(
            source=Workflow, label=_('Internal name'),
            attribute='internal_name'
        )
        SourceColumn(
            source=Workflow, label=_('Initial state'),
            func=lambda context: context['object'].get_initial_state() or _('None')
        )

        SourceColumn(
            source=WorkflowInstance, label=_('Current state'),
            attribute='get_current_state'
        )
        SourceColumn(
            source=WorkflowInstance, label=_('User'),
            func=lambda context: getattr(
                context['object'].get_last_log_entry(), 'user', _('None')
            )
        )
        SourceColumn(
            source=WorkflowInstance, label=_('Last transition'),
            attribute='get_last_transition'
        )
        SourceColumn(
            source=WorkflowInstance, label=_('Date and time'),
            func=lambda context: getattr(
                context['object'].get_last_log_entry(), 'datetime', _('None')
            )
        )
        SourceColumn(
            source=WorkflowInstance, label=_('Completion'),
            func=lambda context: getattr(
                context['object'].get_current_state(), 'completion', _('None')
            )
        )

        SourceColumn(
            source=WorkflowInstanceLogEntry, label=_('Date and time'),
            attribute='datetime'
        )
        SourceColumn(
            source=WorkflowInstanceLogEntry, label=_('User'), attribute='user'
        )
        SourceColumn(
            source=WorkflowInstanceLogEntry, label=_('Transition'),
            attribute='transition'
        )
        SourceColumn(
            source=WorkflowInstanceLogEntry, label=_('Comment'),
            attribute='comment'
        )

        SourceColumn(
            source=WorkflowState, label=_('Is initial state?'),
            func=lambda context: two_state_template(context['object'].initial)
        )
        SourceColumn(
            source=WorkflowState, label=_('Completion'), attribute='completion'
        )

        SourceColumn(
            source=WorkflowStateAction, label=_('Label'), attribute='label'
        )
        SourceColumn(
            source=WorkflowStateAction, label=_('Enabled?'),
            func=lambda context: two_state_template(context['object'].enabled)
        )
        SourceColumn(
            source=WorkflowStateAction, label=_('When?'),
            attribute='get_when_display'
        )
        SourceColumn(
            source=WorkflowStateAction, label=_('Action type'),
            attribute='get_class_label'
        )

        SourceColumn(
            source=WorkflowTransition, label=_('Origin state'),
            attribute='origin_state'
        )
        SourceColumn(
            source=WorkflowTransition, label=_('Destination state'),
            attribute='destination_state'
        )
        SourceColumn(
            source=WorkflowTransition, label=_('Triggers'),
            func=lambda context: widget_transition_events(
                transition=context['object']
            )
        )

        app.conf.CELERY_QUEUES.extend(
            (
                Queue(
                    'document_states', Exchange('document_states'),
                    routing_key='document_states'
                ),
            )
        )

        app.conf.CELERY_ROUTES.update(
            {
                'document_states.tasks.task_launch_all_workflows': {
                    'queue': 'document_states'
                },
            }
        )

        menu_facet.bind_links(
            links=(link_document_workflow_instance_list,), sources=(Document,)
        )
        menu_main.bind_links(links=(link_workflow_list,), position=10)
        menu_object.bind_links(
            links=(
                link_setup_workflow_states, link_setup_workflow_transitions,
                link_setup_workflow_document_types, link_setup_workflow_edit,
                link_acl_list, link_workflow_preview,
                link_setup_workflow_delete
            ), sources=(Workflow,)
        )
        menu_object.bind_links(
            links=(
                link_setup_workflow_state_edit,
                link_setup_workflow_state_action_list,
                link_setup_workflow_state_delete
            ), sources=(WorkflowState,)
        )
        menu_object.bind_links(
            links=(
                link_setup_workflow_transition_edit,
                link_workflow_instance_transition_events, link_acl_list,
                link_setup_workflow_transition_delete
            ), sources=(WorkflowTransition,)
        )
        menu_object.bind_links(
            links=(
                link_workflow_instance_detail,
                link_workflow_instance_transition
            ), sources=(WorkflowInstance,)
        )
        menu_object.bind_links(
            links=(
                link_workflow_document_list, link_workflow_state_list,
            ), sources=(WorkflowRuntimeProxy,)
        )
        menu_object.bind_links(
            links=(
                link_workflow_state_document_list,
            ), sources=(WorkflowStateRuntimeProxy,)
        )
        menu_object.bind_links(
            links=(
                link_setup_workflow_state_action_edit,
                link_object_error_list,
                link_setup_workflow_state_action_delete,
            ), sources=(WorkflowStateAction,)
        )

        menu_secondary.bind_links(
            links=(link_setup_workflow_list, link_setup_workflow_create),
            sources=(
                Workflow, 'document_states:setup_workflow_create',
                'document_states:setup_workflow_list'
            )
        )
        menu_secondary.bind_links(
            links=(link_workflow_list,),
            sources=(
                WorkflowRuntimeProxy,
            )
        )
        menu_secondary.bind_links(
            links=(link_setup_workflow_state_action_selection,),
            sources=(
                WorkflowState,
            )
        )
        menu_setup.bind_links(links=(link_setup_workflow_list,))
        menu_sidebar.bind_links(
            links=(
                link_setup_workflow_state_create,
                link_setup_workflow_transition_create
            ), sources=(Workflow,)
        )
        menu_tools.bind_links(links=(link_tool_launch_all_workflows,))

        post_save.connect(
            launch_workflow, dispatch_uid='launch_workflow', sender=Document
        )

        # Index updating

        post_save.connect(
            handler_index_document,
            dispatch_uid='handler_index_document_save',
            sender=WorkflowInstanceLogEntry
        )
        post_save.connect(
            handler_trigger_transition,
            dispatch_uid='document_states_handler_trigger_transition',
            sender=Action
        )
