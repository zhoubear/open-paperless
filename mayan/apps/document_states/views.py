from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.core.files.base import ContentFile
from django.db.utils import IntegrityError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from acls.models import AccessControlList
from common.views import (
    AssignRemoveView, ConfirmView, FormView, SingleObjectCreateView,
    SingleObjectDeleteView, SingleObjectDetailView,
    SingleObjectDynamicFormCreateView, SingleObjectDynamicFormEditView,
    SingleObjectDownloadView, SingleObjectEditView, SingleObjectListView
)
from documents.models import Document
from documents.views import DocumentListView
from events.classes import Event
from events.models import EventType

from .classes import WorkflowAction
from .forms import (
    WorkflowActionSelectionForm, WorkflowForm, WorkflowInstanceTransitionForm,
    WorkflowPreviewForm, WorkflowStateActionDynamicForm, WorkflowStateForm,
    WorkflowTransitionForm, WorkflowTransitionTriggerEventRelationshipFormSet
)
from .models import (
    Workflow, WorkflowInstance, WorkflowState, WorkflowStateAction,
    WorkflowTransition, WorkflowRuntimeProxy, WorkflowStateRuntimeProxy,
)
from .permissions import (
    permission_workflow_create, permission_workflow_delete,
    permission_workflow_edit, permission_workflow_tools,
    permission_workflow_view,
)
from .tasks import task_launch_all_workflows


class DocumentWorkflowInstanceListView(SingleObjectListView):
    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_workflow_view, user=request.user,
            obj=self.get_document()
        )

        return super(
            DocumentWorkflowInstanceListView, self
        ).dispatch(request, *args, **kwargs)

    def get_document(self):
        return get_object_or_404(Document, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'hide_link': True,
            'object': self.get_document(),
            'title': _(
                'Workflows for document: %s'
            ) % self.get_document(),
        }

    def get_object_list(self):
        return self.get_document().workflows.all()


class WorkflowInstanceDetailView(SingleObjectListView):
    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_workflow_view, user=request.user,
            obj=self.get_workflow_instance().document
        )

        return super(
            WorkflowInstanceDetailView, self
        ).dispatch(request, *args, **kwargs)

    def get_extra_context(self):
        return {
            'hide_object': True,
            'navigation_object_list': ('object', 'workflow_instance'),
            'object': self.get_workflow_instance().document,
            'title': _('Detail of workflow: %(workflow)s') % {
                'workflow': self.get_workflow_instance()
            },
            'workflow_instance': self.get_workflow_instance(),
        }

    def get_object_list(self):
        return self.get_workflow_instance().log_entries.order_by('-datetime')

    def get_workflow_instance(self):
        return get_object_or_404(WorkflowInstance, pk=self.kwargs['pk'])


class WorkflowInstanceTransitionView(FormView):
    form_class = WorkflowInstanceTransitionForm
    template_name = 'appearance/generic_form.html'

    def form_valid(self, form):
        self.get_workflow_instance().do_transition(
            comment=form.cleaned_data['comment'],
            transition=form.cleaned_data['transition'], user=self.request.user
        )
        messages.success(
            self.request, _(
                'Document "%s" transitioned successfully'
            ) % self.get_workflow_instance().document
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_extra_context(self):
        return {
            'navigation_object_list': ('object', 'workflow_instance'),
            'object': self.get_workflow_instance().document,
            'submit_label': _('Submit'),
            'title': _(
                'Do transition for workflow: %s'
            ) % self.get_workflow_instance(),
            'workflow_instance': self.get_workflow_instance(),
        }

    def get_form_extra_kwargs(self):
        return {
            'user': self.request.user,
            'workflow_instance': self.get_workflow_instance()
        }

    def get_success_url(self):
        return self.get_workflow_instance().get_absolute_url()

    def get_workflow_instance(self):
        return get_object_or_404(WorkflowInstance, pk=self.kwargs['pk'])


# Setup

class SetupWorkflowListView(SingleObjectListView):
    extra_context = {
        'title': _('Workflows'),
        'hide_object': True,
    }
    model = Workflow
    view_permission = permission_workflow_view


class SetupWorkflowCreateView(SingleObjectCreateView):
    form_class = WorkflowForm
    model = Workflow
    view_permission = permission_workflow_create
    post_action_redirect = reverse_lazy('document_states:setup_workflow_list')


class SetupWorkflowEditView(SingleObjectEditView):
    form_class = WorkflowForm
    model = Workflow
    view_permission = permission_workflow_edit
    post_action_redirect = reverse_lazy('document_states:setup_workflow_list')


class SetupWorkflowDeleteView(SingleObjectDeleteView):
    model = Workflow
    view_permission = permission_workflow_delete
    post_action_redirect = reverse_lazy('document_states:setup_workflow_list')


class SetupWorkflowDocumentTypesView(AssignRemoveView):
    decode_content_type = True
    object_permission = permission_workflow_edit
    left_list_title = _('Available document types')
    right_list_title = _('Document types assigned this workflow')

    def add(self, item):
        self.get_object().document_types.add(item)
        # TODO: add task launching this workflow for all the document types
        # of item

    def get_extra_context(self):
        return {
            'title': _(
                'Document types assigned the workflow: %s'
            ) % self.get_object(),
            'object': self.get_object(),
        }

    def get_object(self):
        return get_object_or_404(Workflow, pk=self.kwargs['pk'])

    def left_list(self):
        return AssignRemoveView.generate_choices(
            self.get_object().get_document_types_not_in_workflow()
        )

    def right_list(self):
        return AssignRemoveView.generate_choices(
            self.get_object().document_types.all()
        )

    def remove(self, item):
        self.get_object().document_types.remove(item)
        # TODO: add task deleting this workflow for all the document types of
        # item


class SetupWorkflowStateListView(SingleObjectListView):
    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_workflow_view, user=request.user,
            obj=self.get_workflow()
        )

        return super(
            SetupWorkflowStateListView, self
        ).dispatch(request, *args, **kwargs)

    def get_extra_context(self):
        return {
            'hide_link': True,
            'object': self.get_workflow(),
            'title': _('States of workflow: %s') % self.get_workflow()
        }

    def get_object_list(self):
        return self.get_workflow().states.all()

    def get_workflow(self):
        return get_object_or_404(Workflow, pk=self.kwargs['pk'])


class SetupWorkflowStateActionCreateView(SingleObjectDynamicFormCreateView):
    form_class = WorkflowStateActionDynamicForm
    object_permission = permission_workflow_edit

    def get_class(self):
        try:
            return WorkflowAction.get(name=self.kwargs['class_path'])
        except KeyError:
            raise Http404(
                '{} class not found'.format(self.kwargs['class_path'])
            )

    def get_extra_context(self):
        return {
            'navigation_object_list': ('object', 'workflow'),
            'object': self.get_object(),
            'title': _(
                'Create a "%s" workflow action'
            ) % self.get_class().label,
            'workflow': self.get_object().workflow
        }

    def get_form_extra_kwargs(self):
        return {
            'request': self.request,
            'action_path': self.kwargs['class_path']
        }

    def get_form_schema(self):
        return self.get_class()().get_form_schema(request=self.request)

    def get_instance_extra_data(self):
        return {
            'action_path': self.kwargs['class_path'],
            'state': self.get_object()
        }

    def get_object(self):
        return get_object_or_404(WorkflowState, pk=self.kwargs['pk'])

    def get_post_action_redirect(self):
        return reverse(
            'document_states:setup_workflow_state_action_list',
            args=(self.get_object().pk,)
        )


class SetupWorkflowStateActionDeleteView(SingleObjectDeleteView):
    model = WorkflowStateAction
    object_permission = permission_workflow_edit

    def get_extra_context(self):
        return {
            'navigation_object_list': (
                'object', 'workflow_state', 'workflow'
            ),
            'object': self.get_object(),
            'title': _('Delete workflow state action: %s') % self.get_object(),
            'workflow': self.get_object().state.workflow,
            'workflow_state': self.get_object().state,
        }

    def get_post_action_redirect(self):
        return reverse(
            'document_states:setup_workflow_state_action_list',
            args=(self.get_object().state.pk,)
        )


class SetupWorkflowStateActionEditView(SingleObjectDynamicFormEditView):
    form_class = WorkflowStateActionDynamicForm
    model = WorkflowStateAction
    object_permission = permission_workflow_edit

    def get_extra_context(self):
        return {
            'navigation_object_list': (
                'object', 'workflow_state', 'workflow'
            ),
            'object': self.get_object(),
            'title': _('Edit workflow state action: %s') % self.get_object(),
            'workflow': self.get_object().state.workflow,
            'workflow_state': self.get_object().state,
        }

    def get_form_extra_kwargs(self):
        return {
            'request': self.request,
            'action_path': self.get_object().action_path,
        }

    def get_form_schema(self):
        return self.get_object().get_class_instance().get_form_schema(
            request=self.request
        )


class SetupWorkflowStateActionListView(SingleObjectListView):
    object_permission = permission_workflow_edit

    def dispatch(self, request, *args, **kwargs):
        messages.warning(
            request, _(
                'This is a feature preview. Things might not work as expect.'
            )
        )

        return super(
            SetupWorkflowStateActionListView, self
        ).dispatch(request, *args, **kwargs)

    def get_extra_context(self):
        return {
            'hide_object': True,
            'navigation_object_list': ('object', 'workflow'),
            'object': self.get_workflow_state(),
            'title': _(
                'Actions for workflow state: %s'
            ) % self.get_workflow_state(),
            'workflow': self.get_workflow_state().workflow,
        }

    def get_form_schema(self):
        return {'fields': self.get_class().fields}

    def get_object_list(self):
        return self.get_workflow_state().actions.all()

    def get_workflow_state(self):
        return get_object_or_404(WorkflowState, pk=self.kwargs['pk'])


class SetupWorkflowStateActionSelectionView(FormView):
    form_class = WorkflowActionSelectionForm
    view_permission = permission_workflow_edit

    def form_valid(self, form):
        klass = form.cleaned_data['klass']
        return HttpResponseRedirect(
            reverse(
                'document_states:setup_workflow_state_action_create',
                args=(self.get_object().pk, klass,),
            )
        )

    def get_extra_context(self):
        return {
            'navigation_object_list': (
                'object', 'workflow'
            ),
            'object': self.get_object(),
            'title': _('New workflow state action selection'),
            'workflow': self.get_object().workflow,
        }

    def get_object(self):
        return get_object_or_404(WorkflowState, pk=self.kwargs['pk'])


class SetupWorkflowStateCreateView(SingleObjectCreateView):
    form_class = WorkflowStateForm
    view_permission = permission_workflow_edit

    def get_extra_context(self):
        return {
            'object': self.get_workflow(),
            'title': _(
                'Create states for workflow: %s'
            ) % self.get_workflow()
        }

    def get_workflow(self):
        return get_object_or_404(Workflow, pk=self.kwargs['pk'])

    def get_object_list(self):
        return self.get_workflow().states.all()

    def get_success_url(self):
        return reverse(
            'document_states:setup_workflow_states', args=(self.kwargs['pk'],)
        )

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.workflow = self.get_workflow()
        self.object.save()
        return super(SetupWorkflowStateCreateView, self).form_valid(form)


class SetupWorkflowStateDeleteView(SingleObjectDeleteView):
    model = WorkflowState
    view_permission = permission_workflow_edit

    def get_extra_context(self):
        return {
            'navigation_object_list': ('object', 'workflow_instance'),
            'object': self.get_object(),
            'workflow_instance': self.get_object().workflow,
        }

    def get_success_url(self):
        return reverse(
            'document_states:setup_workflow_states',
            args=(self.get_object().workflow.pk,)
        )


class SetupWorkflowStateEditView(SingleObjectEditView):
    form_class = WorkflowStateForm
    model = WorkflowState
    view_permission = permission_workflow_edit

    def get_extra_context(self):
        return {
            'navigation_object_list': ('object', 'workflow_instance'),
            'object': self.get_object(),
            'workflow_instance': self.get_object().workflow,
        }

    def get_success_url(self):
        return reverse(
            'document_states:setup_workflow_states',
            args=(self.get_object().workflow.pk,)
        )


# Transitions


class SetupWorkflowTransitionListView(SingleObjectListView):
    view_permission = permission_workflow_view

    def get_extra_context(self):
        return {
            'hide_link': True,
            'object': self.get_workflow(),
            'title': _(
                'Transitions of workflow: %s'
            ) % self.get_workflow()
        }

    def get_object_list(self):
        return self.get_workflow().transitions.all()

    def get_workflow(self):
        return get_object_or_404(Workflow, pk=self.kwargs['pk'])


class SetupWorkflowTransitionCreateView(SingleObjectCreateView):
    form_class = WorkflowTransitionForm
    view_permission = permission_workflow_edit

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.workflow = self.get_workflow()
        try:
            self.object.save()
        except IntegrityError:
            messages.error(
                self.request, _('Unable to save transition; integrity error.')
            )
            return super(
                SetupWorkflowTransitionCreateView, self
            ).form_invalid(form)
        else:
            return HttpResponseRedirect(self.get_success_url())

    def get_extra_context(self):
        return {
            'object': self.get_workflow(),
            'title': _(
                'Create transitions for workflow: %s'
            ) % self.get_workflow()
        }

    def get_form_kwargs(self):
        kwargs = super(
            SetupWorkflowTransitionCreateView, self
        ).get_form_kwargs()
        kwargs['workflow'] = self.get_workflow()
        return kwargs

    def get_object_list(self):
        return self.get_workflow().transitions.all()

    def get_success_url(self):
        return reverse(
            'document_states:setup_workflow_transitions',
            args=(self.kwargs['pk'],)
        )

    def get_workflow(self):
        return get_object_or_404(Workflow, pk=self.kwargs['pk'])


class SetupWorkflowTransitionDeleteView(SingleObjectDeleteView):
    model = WorkflowTransition
    view_permission = permission_workflow_edit

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'navigation_object_list': ('object', 'workflow_instance'),
            'workflow_instance': self.get_object().workflow,
        }

    def get_success_url(self):
        return reverse(
            'document_states:setup_workflow_transitions',
            args=(self.get_object().workflow.pk,)
        )


class SetupWorkflowTransitionEditView(SingleObjectEditView):
    form_class = WorkflowTransitionForm
    model = WorkflowTransition
    view_permission = permission_workflow_edit

    def get_extra_context(self):
        return {
            'navigation_object_list': ('object', 'workflow_instance'),
            'object': self.get_object(),
            'workflow_instance': self.get_object().workflow,
        }

    def get_form_kwargs(self):
        kwargs = super(
            SetupWorkflowTransitionEditView, self
        ).get_form_kwargs()
        kwargs['workflow'] = self.get_object().workflow
        return kwargs

    def get_success_url(self):
        return reverse(
            'document_states:setup_workflow_transitions',
            args=(self.get_object().workflow.pk,)
        )


class WorkflowListView(SingleObjectListView):
    view_permission = permission_workflow_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'title': _('Workflows')
        }

    def get_object_list(self):
        return WorkflowRuntimeProxy.objects.all()


class WorkflowDocumentListView(DocumentListView):
    def dispatch(self, request, *args, **kwargs):
        self.workflow = get_object_or_404(
            WorkflowRuntimeProxy, pk=self.kwargs['pk']
        )

        AccessControlList.objects.check_access(
            permissions=permission_workflow_view, user=request.user,
            obj=self.workflow
        )

        return super(
            WorkflowDocumentListView, self
        ).dispatch(request, *args, **kwargs)

    def get_document_queryset(self):
        return Document.objects.filter(workflows__workflow=self.workflow)

    def get_extra_context(self):
        context = super(WorkflowDocumentListView, self).get_extra_context()
        context.update(
            {
                'object': self.workflow,
                'title': _('Documents with the workflow: %s') % self.workflow
            }
        )
        return context


class WorkflowStateDocumentListView(DocumentListView):
    def get_document_queryset(self):
        return self.get_workflow_state().get_documents()

    def get_extra_context(self):
        workflow_state = self.get_workflow_state()
        context = super(WorkflowStateDocumentListView, self).get_extra_context()
        context.update(
            {
                'object': workflow_state,
                'navigation_object_list': ('object', 'workflow'),
                'workflow': WorkflowRuntimeProxy.objects.get(
                    pk=workflow_state.workflow.pk
                ),
                'title': _(
                    'Documents in the workflow "%s", state "%s"'
                ) % (
                    workflow_state.workflow, workflow_state
                )
            }
        )
        return context

    def get_workflow_state(self):
        workflow_state = get_object_or_404(
            WorkflowStateRuntimeProxy, pk=self.kwargs['pk']
        )

        AccessControlList.objects.check_access(
            permissions=permission_workflow_view, user=self.request.user,
            obj=workflow_state.workflow
        )

        return workflow_state


class WorkflowStateListView(SingleObjectListView):
    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_workflow_view, user=request.user,
            obj=self.get_workflow()
        )

        return super(
            WorkflowStateListView, self
        ).dispatch(request, *args, **kwargs)

    def get_extra_context(self):
        return {
            'hide_columns': True,
            'hide_link': True,
            'object': self.get_workflow(),
            'title': _('States of workflow: %s') % self.get_workflow()
        }

    def get_object_list(self):
        return WorkflowStateRuntimeProxy.objects.filter(
            workflow=self.get_workflow()
        )

    def get_workflow(self):
        return get_object_or_404(WorkflowRuntimeProxy, pk=self.kwargs['pk'])


class SetupWorkflowTransitionTriggerEventListView(FormView):
    form_class = WorkflowTransitionTriggerEventRelationshipFormSet
    submodel = EventType

    def dispatch(self, *args, **kwargs):
        messages.warning(
            self.request, _(
                'This is a feature preview. Things might not work as expect.'
            )
        )

        AccessControlList.objects.check_access(
            permissions=permission_workflow_edit,
            user=self.request.user, obj=self.get_object().workflow
        )

        Event.refresh()
        return super(
            SetupWorkflowTransitionTriggerEventListView, self
        ).dispatch(*args, **kwargs)

    def form_valid(self, form):
        try:
            for instance in form:
                instance.save()
        except Exception as exception:
            messages.error(
                self.request,
                _(
                    'Error updating workflow transition trigger events; %s'
                ) % exception
            )
        else:
            messages.success(
                self.request, _(
                    'Workflow transition trigger events updated successfully'
                )
            )

        return super(
            SetupWorkflowTransitionTriggerEventListView, self
        ).form_valid(form=form)

    def get_object(self):
        return get_object_or_404(WorkflowTransition, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'form_display_mode_table': True,
            'navigation_object_list': ('object', 'workflow'),
            'object': self.get_object(),
            'title': _(
                'Workflow transition trigger events for: %s'
            ) % self.get_object(),
            'workflow': self.get_object().workflow,
        }

    def get_initial(self):
        obj = self.get_object()
        initial = []

        # Return the queryset by name from the sorted list of the class
        event_type_ids = [event_type.name for event_type in Event.all()]
        event_type_queryset = EventType.objects.filter(name__in=event_type_ids)

        for event_type in event_type_queryset:
            initial.append({
                'transition': obj,
                'event_type': event_type,
            })
        return initial

    def get_post_action_redirect(self):
        return reverse(
            'document_states:setup_workflow_transitions',
            args=(self.get_object().workflow.pk,)
        )


class ToolLaunchAllWorkflows(ConfirmView):
    extra_context = {
        'title': _('Launch all workflows?')
    }
    view_permission = permission_workflow_tools

    def view_action(self):
        task_launch_all_workflows.apply_async()
        messages.success(
            self.request, _('Workflow launch queued successfully.')
        )


class WorkflowImageView(SingleObjectDownloadView):
    attachment = False
    model = Workflow
    object_permission = permission_workflow_view

    def get_file(self):
        workflow = self.get_object()
        return ContentFile(workflow.render(), name=workflow.label)

    def get_mimetype(self):
        return 'image'


class WorkflowPreviewView(SingleObjectDetailView):
    form_class = WorkflowPreviewForm
    model = Workflow
    object_permission = permission_workflow_view

    def get_extra_context(self):
        return {
            'hide_labels': True,
            'title': _('Preview of: %s') % self.get_object()
        }
