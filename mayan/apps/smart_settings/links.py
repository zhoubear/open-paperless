from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Link

from .permissions import permission_settings_view

link_namespace_list = Link(
    icon='fa fa-sliders', permissions=(permission_settings_view,),
    text=_('Settings'), view='settings:namespace_list'
)
link_namespace_detail = Link(
    permissions=(permission_settings_view,), text=_('Settings'),
    view='settings:namespace_detail', args='resolved_object.name'
)
