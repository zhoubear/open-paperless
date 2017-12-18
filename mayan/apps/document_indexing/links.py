from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Link

from .permissions import (
    permission_document_indexing_create, permission_document_indexing_edit,
    permission_document_indexing_delete, permission_document_indexing_rebuild,
)


def is_not_root_node(context):
    return not context['resolved_object'].is_root_node()


link_document_index_list = Link(
    icon='fa fa-list-ul', text=_('Indexes'),
    view='indexing:document_index_list', args='resolved_object.pk'
)
link_index_main_menu = Link(
    icon='fa fa-list-ul', text=_('Indexes'), view='indexing:index_list'
)
link_index_setup = Link(
    icon='fa fa-list-ul', text=_('Indexes'), view='indexing:index_setup_list'
)
link_index_setup_list = Link(
    text=_('Indexes'), view='indexing:index_setup_list'
)
link_index_setup_create = Link(
    permissions=(permission_document_indexing_create,), text=_('Create index'),
    view='indexing:index_setup_create'
)
link_index_setup_edit = Link(
    permissions=(permission_document_indexing_edit,), text=_('Edit'),
    view='indexing:index_setup_edit', args='resolved_object.pk'
)
link_index_setup_delete = Link(
    permissions=(permission_document_indexing_delete,), tags='dangerous',
    text=_('Delete'), view='indexing:index_setup_delete',
    args='resolved_object.pk'
)
link_index_setup_view = Link(
    permissions=(permission_document_indexing_edit,), text=_('Tree template'),
    view='indexing:index_setup_view', args='resolved_object.pk'
)
link_index_setup_document_types = Link(
    permissions=(permission_document_indexing_edit,), text=_('Document types'),
    view='indexing:index_setup_document_types', args='resolved_object.pk'
)
link_rebuild_index_instances = Link(
    icon='fa fa-list-ul',
    description=_(
        'Deletes and creates from scratch all the document indexes.'
    ),
    permissions=(permission_document_indexing_rebuild,),
    text=_('Rebuild indexes'), view='indexing:rebuild_index_instances'
)
link_template_node_create = Link(
    text=_('New child node'), view='indexing:template_node_create',
    args='resolved_object.pk'
)
link_template_node_edit = Link(
    condition=is_not_root_node, text=_('Edit'),
    view='indexing:template_node_edit', args='resolved_object.pk'
)
link_template_node_delete = Link(
    condition=is_not_root_node, tags='dangerous', text=_('Delete'),
    view='indexing:template_node_delete', args='resolved_object.pk'
)
