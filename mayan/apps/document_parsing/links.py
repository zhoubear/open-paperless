from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Link

from .permissions import permission_content_view, permission_parse_document

link_document_content = Link(
    args='resolved_object.id', icon='fa fa-font',
    permissions=(permission_content_view,), text=_('Content'),
    view='document_parsing:document_content',
)
link_document_parsing_errors_list = Link(
    args='resolved_object.id', icon='fa fa-file-text-o',
    permissions=(permission_content_view,), text=_('Parsing errors'),
    view='document_parsing:document_parsing_error_list'
)
link_document_content_download = Link(
    args='resolved_object.id', icon='fa fa-file-text-o',
    permissions=(permission_content_view,), text=_('Download content'),
    view='document_parsing:document_content_download'
)
link_document_submit_multiple = Link(
    text=_('Submit for parsing'),
    view='document_parsing:document_submit_multiple'
)
link_document_submit = Link(
    args='resolved_object.id', permissions=(permission_parse_document,),
    text=_('Submit for parsing'), view='document_parsing:document_submit'
)
link_document_type_submit = Link(
    icon='fa fa-crosshairs', text=_('Parse documents per type'),
    view='document_parsing:document_type_submit'
)
link_error_list = Link(
    icon='fa fa-file-text-o', permissions=(permission_content_view,),
    text=_('Parsing errors'), view='document_parsing:error_list'
)
