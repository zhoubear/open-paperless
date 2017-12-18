from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Link

from .permissions import (
    permission_workflow_create, permission_workflow_delete,
    permission_workflow_edit, permission_workflow_tools,
    permission_workflow_view,
)

link_document_workflow_instance_list = Link(
    icon='fa fa-sitemap', permissions=(permission_workflow_view,),
    text=_('Workflows'),
    view='document_states:document_workflow_instance_list',
    args='resolved_object.pk'
)
link_setup_workflow_create = Link(
    permissions=(permission_workflow_create,), text=_('Create workflow'),
    view='document_states:setup_workflow_create'
)
link_setup_workflow_delete = Link(
    permissions=(permission_workflow_delete,), tags='dangerous',
    text=_('Delete'), view='document_states:setup_workflow_delete',
    args='resolved_object.pk'
)
link_setup_workflow_document_types = Link(
    permissions=(permission_workflow_edit,), text=_('Document types'),
    view='document_states:setup_workflow_document_types',
    args='resolved_object.pk'
)
link_setup_workflow_edit = Link(
    permissions=(permission_workflow_edit,), text=_('Edit'),
    view='document_states:setup_workflow_edit', args='resolved_object.pk'
)
link_setup_workflow_list = Link(
    permissions=(permission_workflow_view,), icon='fa fa-sitemap',
    text=_('Workflows'), view='document_states:setup_workflow_list'
)
link_setup_workflow_state_action_delete = Link(
    args='resolved_object.pk', permissions=(permission_workflow_edit,),
    tags='dangerous', text=_('Delete'),
    view='document_states:setup_workflow_state_action_delete',
)
link_setup_workflow_state_action_edit = Link(
    args='resolved_object.pk', permissions=(permission_workflow_edit,),
    text=_('Edit'), view='document_states:setup_workflow_state_action_edit',
)
link_setup_workflow_state_action_list = Link(
    args='resolved_object.pk', permissions=(permission_workflow_edit,),
    text=_('Actions'),
    view='document_states:setup_workflow_state_action_list',
)
link_setup_workflow_state_action_selection = Link(
    args='resolved_object.pk', permissions=(permission_workflow_edit,),
    text=_('Create action'),
    view='document_states:setup_workflow_state_action_selection',
)
link_setup_workflow_state_create = Link(
    permissions=(permission_workflow_edit,), text=_('Create state'),
    view='document_states:setup_workflow_state_create',
    args='resolved_object.pk'
)
link_setup_workflow_state_delete = Link(
    permissions=(permission_workflow_edit,), tags='dangerous',
    text=_('Delete'), view='document_states:setup_workflow_state_delete',
    args='object.pk'
)
link_setup_workflow_state_edit = Link(
    permissions=(permission_workflow_edit,), text=_('Edit'),
    view='document_states:setup_workflow_state_edit', args='resolved_object.pk'
)
link_setup_workflow_states = Link(
    permissions=(permission_workflow_view,), text=_('States'),
    view='document_states:setup_workflow_states', args='resolved_object.pk'
)
link_setup_workflow_transition_create = Link(
    permissions=(permission_workflow_edit,), text=_('Create transition'),
    view='document_states:setup_workflow_transition_create',
    args='resolved_object.pk'
)
link_setup_workflow_transition_delete = Link(
    permissions=(permission_workflow_edit,), tags='dangerous',
    text=_('Delete'), view='document_states:setup_workflow_transition_delete',
    args='resolved_object.pk'
)
link_setup_workflow_transition_edit = Link(
    permissions=(permission_workflow_edit,), text=_('Edit'),
    view='document_states:setup_workflow_transition_edit',
    args='resolved_object.pk'
)
link_setup_workflow_transitions = Link(
    permissions=(permission_workflow_view,), text=_('Transitions'),
    view='document_states:setup_workflow_transitions',
    args='resolved_object.pk'
)
link_tool_launch_all_workflows = Link(
    icon='fa fa-sitemap',
    permissions=(permission_workflow_tools,),
    text=_('Launch all workflows'),
    view='document_states:tool_launch_all_workflows'
)
link_workflow_instance_detail = Link(
    permissions=(permission_workflow_view,), text=_('Detail'),
    view='document_states:workflow_instance_detail', args='resolved_object.pk'
)
link_workflow_instance_transition = Link(
    text=_('Transition'),
    view='document_states:workflow_instance_transition',
    args='resolved_object.pk'
)
link_workflow_document_list = Link(
    permissions=(permission_workflow_view,), text=_('Workflow documents'),
    view='document_states:workflow_document_list', args='resolved_object.pk'
)
link_workflow_list = Link(
    permissions=(permission_workflow_view,), icon='fa fa-sitemap',
    text=_('Workflows'), view='document_states:workflow_list'
)
link_workflow_state_document_list = Link(
    permissions=(permission_workflow_view,),
    text=_('State documents'),
    view='document_states:workflow_state_document_list',
    args='resolved_object.pk'
)
link_workflow_state_list = Link(
    permissions=(permission_workflow_view,),
    text=_('States'), view='document_states:workflow_state_list',
    args='resolved_object.pk'
)
link_workflow_instance_transition_events = Link(
    args='resolved_object.pk', permissions=(permission_workflow_edit,),
    text=_('Transition triggers'),
    view='document_states:setup_workflow_instance_transition_events'
)
link_workflow_preview = Link(
    args='resolved_object.pk', permissions=(permission_workflow_view,),
    text=_('Preview'), view='document_states:workflow_preview'
)
