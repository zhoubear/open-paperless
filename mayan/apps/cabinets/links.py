from __future__ import absolute_import, unicode_literals

import copy

from django.utils.translation import ugettext_lazy as _

from acls.links import link_acl_list
from documents.permissions import permission_document_view
from navigation import Link

from .permissions import (
    permission_cabinet_add_document, permission_cabinet_create,
    permission_cabinet_delete, permission_cabinet_edit,
    permission_cabinet_view, permission_cabinet_remove_document
)

# Document links

link_document_cabinet_list = Link(
    icon='fa fa-columns', permissions=(permission_document_view,),
    text=_('Cabinets'), view='cabinets:document_cabinet_list',
    args='resolved_object.pk'
)
link_document_cabinet_remove = Link(
    args='resolved_object.pk',
    permissions=(permission_cabinet_remove_document,),
    text=_('Remove from cabinets'), view='cabinets:document_cabinet_remove'
)
link_cabinet_add_document = Link(
    permissions=(permission_cabinet_add_document,),
    text=_('Add to cabinets'), view='cabinets:cabinet_add_document',
    args='object.pk'
)
link_cabinet_add_multiple_documents = Link(
    text=_('Add to cabinets'), view='cabinets:cabinet_add_multiple_documents'
)
link_multiple_document_cabinet_remove = Link(
    text=_('Remove from cabinets'),
    view='cabinets:multiple_document_cabinet_remove'
)

# Cabinet links


def cabinet_is_root(context):
    return context[
        'resolved_object'
    ].is_root_node()


link_custom_acl_list = copy.copy(link_acl_list)
link_custom_acl_list.condition = cabinet_is_root

link_cabinet_child_add = Link(
    permissions=(permission_cabinet_create,), text=_('Add new level'),
    view='cabinets:cabinet_child_add', args='object.pk'
)
link_cabinet_create = Link(
    icon='fa fa-plus', permissions=(permission_cabinet_create,),
    text=_('Create cabinet'), view='cabinets:cabinet_create'
)
link_cabinet_delete = Link(
    permissions=(permission_cabinet_delete,), tags='dangerous',
    text=_('Delete'), view='cabinets:cabinet_delete', args='object.pk'
)
link_cabinet_edit = Link(
    permissions=(permission_cabinet_edit,), text=_('Edit'),
    view='cabinets:cabinet_edit', args='object.pk'
)
link_cabinet_list = Link(
    icon='fa fa-columns', text=_('All'), view='cabinets:cabinet_list'
)
link_cabinet_view = Link(
    permissions=(permission_cabinet_view,), text=_('Details'),
    view='cabinets:cabinet_view', args='object.pk'
)
