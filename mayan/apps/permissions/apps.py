from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from common import (
    MayanAppConfig, menu_multi_item, menu_object, menu_secondary, menu_setup
)
from common.signals import perform_upgrade
from rest_api.classes import APIEndPoint

from .handlers import purge_permissions
from .links import (
    link_permission_grant, link_permission_revoke, link_role_create,
    link_role_delete, link_role_edit, link_role_list, link_role_members,
    link_role_permissions
)
from .search import *  # NOQA


class PermissionsApp(MayanAppConfig):
    has_tests = True
    name = 'permissions'
    verbose_name = _('Permissions')

    def ready(self):
        super(PermissionsApp, self).ready()

        Role = self.get_model('Role')

        APIEndPoint(app=self, version_string='1')

        menu_object.bind_links(
            links=(
                link_role_edit, link_role_members, link_role_permissions,
                link_role_delete
            ), sources=(Role,)
        )
        menu_multi_item.bind_links(
            links=(link_permission_grant, link_permission_revoke),
            sources=('permissions:role_permissions',)
        )
        menu_secondary.bind_links(
            links=(link_role_list, link_role_create),
            sources=(Role, 'permissions:role_create', 'permissions:role_list')
        )
        menu_setup.bind_links(links=(link_role_list,))

        perform_upgrade.connect(
            purge_permissions, dispatch_uid='purge_permissions'
        )
