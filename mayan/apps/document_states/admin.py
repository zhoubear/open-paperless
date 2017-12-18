from __future__ import unicode_literals

from django.contrib import admin

from .models import (
    Workflow, WorkflowInstance, WorkflowInstanceLogEntry, WorkflowState,
    WorkflowStateAction, WorkflowTransition
)


class WorkflowInstanceLogEntryInline(admin.TabularInline):
    extra = 1
    model = WorkflowInstanceLogEntry


class WorkflowStateInline(admin.TabularInline):
    model = WorkflowState


class WorkflowTransitionInline(admin.TabularInline):
    model = WorkflowTransition


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    def document_types_list(self, instance):
        return ','.join(
            instance.document_types.values_list('label', flat=True)
        )

    filter_horizontal = ('document_types',)
    inlines = (WorkflowStateInline, WorkflowTransitionInline)
    list_display = ('label', 'internal_name', 'document_types_list')


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    inlines = (WorkflowInstanceLogEntryInline,)
    list_display = (
        'workflow', 'document', 'get_current_state', 'get_last_transition'
    )


@admin.register(WorkflowStateAction)
class WorkflowStateActionAdmin(admin.ModelAdmin):
    list_display = (
        'state', 'label', 'enabled', 'when', 'action_path', 'action_data'
    )
