from __future__ import unicode_literals, absolute_import

from django.utils.translation import ugettext_lazy as _

from navigation import Link

from .permissions import (
    permission_comment_create, permission_comment_delete,
    permission_comment_view
)

link_comment_add = Link(
    permissions=(permission_comment_create,), text=_('Add comment'),
    view='comments:comment_add', args='object.pk'
)
link_comment_delete = Link(
    permissions=(permission_comment_delete,), tags='dangerous',
    text=_('Delete'), view='comments:comment_delete', args='object.pk'
)
link_comments_for_document = Link(
    icon='fa fa-comment', permissions=(permission_comment_view,),
    text=_('Comments'), view='comments:comments_for_document',
    args='resolved_object.pk'
)
