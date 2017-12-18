from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from documents.permissions import permission_document_view
from navigation import Link

from .permissions import (
    permission_smart_link_create, permission_smart_link_delete,
    permission_smart_link_edit, permission_smart_link_view
)

link_smart_link_condition_create = Link(
    permissions=(permission_smart_link_edit,), text=_('Create condition'),
    view='linking:smart_link_condition_create', args='object.pk'
)
link_smart_link_condition_delete = Link(
    permissions=(permission_smart_link_edit,), tags='dangerous',
    text=_('Delete'), view='linking:smart_link_condition_delete',
    args='resolved_object.pk'
)
link_smart_link_condition_edit = Link(
    permissions=(permission_smart_link_edit,), text=_('Edit'),
    view='linking:smart_link_condition_edit', args='resolved_object.pk'
)
link_smart_link_condition_list = Link(
    permissions=(permission_smart_link_edit,), text=_('Conditions'),
    view='linking:smart_link_condition_list', args='object.pk'
)
link_smart_link_create = Link(
    permissions=(permission_smart_link_create,),
    text=_('Create new smart link'), view='linking:smart_link_create'
)
link_smart_link_delete = Link(
    permissions=(permission_smart_link_delete,), tags='dangerous',
    text=_('Delete'), view='linking:smart_link_delete', args='object.pk'
)
link_smart_link_document_types = Link(
    permissions=(permission_smart_link_edit,), text=_('Document types'),
    view='linking:smart_link_document_types', args='object.pk'
)
link_smart_link_edit = Link(
    permissions=(permission_smart_link_edit,), text=_('Edit'),
    view='linking:smart_link_edit', args='object.pk'
)
link_smart_link_instance_view = Link(
    permissions=(permission_smart_link_view,), text=_('Documents'),
    view='linking:smart_link_instance_view', args=(
        'document.pk', 'object.pk',
    )
)
link_smart_link_instances_for_document = Link(
    icon='fa fa-link', permissions=(permission_document_view,),
    text=_('Smart links'), view='linking:smart_link_instances_for_document',
    args='resolved_object.pk'
)
link_smart_link_list = Link(
    permissions=(permission_smart_link_create,), text=_('Smart links'),
    view='linking:smart_link_list'
)
link_smart_link_setup = Link(
    icon='fa fa-link', permissions=(permission_smart_link_create,),
    text=_('Smart links'), view='linking:smart_link_list'
)
