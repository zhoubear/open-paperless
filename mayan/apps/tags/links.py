from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Link

from .permissions import (
    permission_tag_attach, permission_tag_create, permission_tag_delete,
    permission_tag_edit, permission_tag_remove, permission_tag_view
)


link_multiple_documents_tag_remove = Link(
    text=_('Remove tag'), view='tags:multiple_documents_selection_tag_remove'
)
link_multiple_documents_attach_tag = Link(
    text=_('Attach tags'), view='tags:multiple_documents_tag_attach'
)
link_single_document_multiple_tag_remove = Link(
    permissions=(permission_tag_remove,), text=_('Remove tags'),
    view='tags:single_document_multiple_tag_remove', args='object.id'
)
link_tag_attach = Link(
    permissions=(permission_tag_attach,), text=_('Attach tags'),
    view='tags:tag_attach', args='object.pk'
)
link_tag_create = Link(
    icon='fa fa-plus', permissions=(permission_tag_create,),
    text=_('Create new tag'), view='tags:tag_create'
)
link_tag_delete = Link(
    permissions=(permission_tag_delete,), tags='dangerous', text=_('Delete'),
    view='tags:tag_delete', args='object.id'
)
link_tag_edit = Link(
    permissions=(permission_tag_edit,), text=_('Edit'), view='tags:tag_edit',
    args='object.id'
)
link_tag_document_list = Link(
    icon='fa fa-tag', permissions=(permission_tag_view,), text=_('Tags'),
    view='tags:document_tags', args='resolved_object.pk'
)
link_tag_list = Link(icon='fa fa-tag', text=_('All'), view='tags:tag_list')
link_tag_multiple_delete = Link(
    permissions=(permission_tag_delete,), text=_('Delete'),
    view='tags:tag_multiple_delete'
)
link_tag_tagged_item_list = Link(
    text=('Documents'), view='tags:tag_tagged_item_list', args='object.id'
)
