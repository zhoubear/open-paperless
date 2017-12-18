from __future__ import unicode_literals

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from document_indexing.tasks import task_index_document
from events.classes import Event


def handler_index_document(sender, **kwargs):
    task_index_document.apply_async(
        kwargs=dict(
            document_id=kwargs['instance'].workflow_instance.document.pk
        )
    )


def handler_trigger_transition(sender, **kwargs):
    action = kwargs['instance']

    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )
    WorkflowInstance = apps.get_model(
        app_label='document_states', model_name='WorkflowInstance'
    )
    WorkflowTransition = apps.get_model(
        app_label='document_states', model_name='WorkflowTransition'
    )

    trigger_transitions = WorkflowTransition.objects.filter(trigger_events__event_type__name=kwargs['instance'].verb)

    if isinstance(action.target, Document):
        workflow_instances = WorkflowInstance.objects.filter(workflow__transitions__in=trigger_transitions, document=action.target).distinct()
    elif isinstance(action.action_object, Document):
        workflow_instances = WorkflowInstance.objects.filter(workflow__transitions__in=trigger_transitions, document=action.action_object).distinct()
    else:
        workflow_instances = WorkflowInstance.objects.none()

    for workflow_instance in workflow_instances:
        # Select the first transition that is valid for this workflow state
        transition = list(set(trigger_transitions) & set(workflow_instance.get_transition_choices()))[0]

        workflow_instance.do_transition(
            comment=_('Event trigger: %s') % Event.get(name=action.verb).label,
            transition=transition
        )


def launch_workflow(sender, instance, created, **kwargs):
    Workflow = apps.get_model(
        app_label='document_states', model_name='Workflow'
    )

    if created:
        Workflow.objects.launch_for(instance)
