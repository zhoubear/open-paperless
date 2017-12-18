from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Link

link_api = Link(
    icon='fa fa-plug', tags='new_window', text=_('REST API'),
    view='rest_api:api_root'
)
link_api_documentation = Link(
    icon='fa fa-book', tags='new_window', text=_('API Documentation'),
    view='django.swagger.base.view'
)
