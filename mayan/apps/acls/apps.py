from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from common import MayanAppConfig, menu_object, menu_sidebar
from navigation import SourceColumn
from rest_api.classes import APIEndPoint

from .links import link_acl_create, link_acl_delete, link_acl_permissions


class ACLsApp(MayanAppConfig):
    has_tests = True
    name = 'acls'
    verbose_name = _('ACLs')

    def ready(self):
        super(ACLsApp, self).ready()

        APIEndPoint(app=self, version_string='1')

        AccessControlList = self.get_model('AccessControlList')

        SourceColumn(
            source=AccessControlList, label=_('Permissions'),
            attribute='get_permission_titles'
        )
        SourceColumn(
            source=AccessControlList, label=_('Role'), attribute='role'
        )

        menu_object.bind_links(
            links=(link_acl_permissions, link_acl_delete),
            sources=(AccessControlList,)
        )
        menu_sidebar.bind_links(
            links=(link_acl_create,), sources=('acls:acl_list',)
        )
