from __future__ import unicode_literals

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from acls import ModelPermission
from acls.links import link_acl_list
from acls.permissions import permission_acl_edit, permission_acl_view
from common import (
    MayanAppConfig, menu_facet, menu_object, menu_secondary, menu_setup,
    menu_sidebar
)
from common.widgets import two_state_template
from navigation import SourceColumn
from rest_api.classes import APIEndPoint

from .links import (
    link_smart_link_create, link_smart_link_condition_create,
    link_smart_link_condition_delete, link_smart_link_condition_edit,
    link_smart_link_condition_list, link_smart_link_delete,
    link_smart_link_document_types, link_smart_link_edit,
    link_smart_link_instance_view, link_smart_link_instances_for_document,
    link_smart_link_list, link_smart_link_setup
)
from .permissions import (
    permission_smart_link_delete, permission_smart_link_edit,
    permission_smart_link_view
)


class LinkingApp(MayanAppConfig):
    has_tests = True
    name = 'linking'
    verbose_name = _('Linking')

    def ready(self):
        super(LinkingApp, self).ready()

        APIEndPoint(app=self, version_string='1')

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )

        ResolvedSmartLink = self.get_model('ResolvedSmartLink')
        SmartLink = self.get_model('SmartLink')
        SmartLinkCondition = self.get_model('SmartLinkCondition')

        ModelPermission.register(
            model=SmartLink, permissions=(
                permission_acl_edit, permission_acl_view,
                permission_smart_link_delete, permission_smart_link_edit,
                permission_smart_link_view
            )
        )

        SourceColumn(
            source=ResolvedSmartLink, label=_('Label'),
            func=lambda context: context['object'].get_dynamic_label(
                context['document']
            )
        )

        SourceColumn(
            source=SmartLink, label=_('Dynamic label'),
            attribute='dynamic_label'
        )
        SourceColumn(
            source=SmartLink, label=_('Enabled'),
            func=lambda context: two_state_template(context['object'].enabled)
        )

        SourceColumn(
            source=SmartLinkCondition, label=_('Enabled'),
            func=lambda context: two_state_template(context['object'].enabled)
        )

        menu_facet.bind_links(
            links=(link_smart_link_instances_for_document,),
            sources=(Document,)
        )
        menu_object.bind_links(
            links=(
                link_smart_link_condition_edit,
                link_smart_link_condition_delete
            ), sources=(SmartLinkCondition,)
        )
        menu_object.bind_links(
            links=(
                link_smart_link_edit, link_smart_link_document_types,
                link_smart_link_condition_list, link_acl_list,
                link_smart_link_delete
            ), sources=(SmartLink,)
        )
        menu_object.bind_links(
            links=(link_smart_link_instance_view,),
            sources=(ResolvedSmartLink,)
        )
        menu_secondary.bind_links(
            links=(link_smart_link_list, link_smart_link_create),
            sources=(
                SmartLink, 'linking:smart_link_list',
                'linking:smart_link_create'
            )
        )
        menu_setup.bind_links(links=(link_smart_link_setup,))
        menu_sidebar.bind_links(
            links=(link_smart_link_condition_create,),
            sources=(
                'linking:smart_link_condition_list',
                'linking:smart_link_condition_create',
                'linking:smart_link_condition_edit',
                'linking:smart_link_condition_delete'
            )
        )
