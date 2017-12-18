from __future__ import unicode_literals

from django.apps import apps
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from common import menu_multi_item, menu_object, menu_secondary, menu_setup
from common.apps import MayanAppConfig
from common.widgets import two_state_template
from metadata import MetadataLookup
from navigation import SourceColumn
from rest_api.classes import APIEndPoint
from rest_api.fields import DynamicSerializerField

from .links import (
    link_group_add, link_group_delete, link_group_edit, link_group_list,
    link_group_members, link_group_setup, link_user_add, link_user_delete,
    link_user_edit, link_user_groups, link_user_list,
    link_user_multiple_delete, link_user_multiple_set_password,
    link_user_set_password, link_user_setup
)
from .search import *  # NOQA


def get_groups():
    Group = apps.get_model(app_label='auth', model_name='Group')
    return ','.join([group.name for group in Group.objects.all()])


def get_users():
    return ','.join(
        [
            user.get_full_name() or user.username
            for user in get_user_model().objects.all()
        ]
    )


class UserManagementApp(MayanAppConfig):
    app_url = 'accounts'
    has_tests = True
    name = 'user_management'
    verbose_name = _('User management')

    def ready(self):
        super(UserManagementApp, self).ready()
        from actstream import registry

        Group = apps.get_model(app_label='auth', model_name='Group')
        User = get_user_model()

        APIEndPoint(app=self, version_string='1')
        DynamicSerializerField.add_serializer(
            klass=get_user_model(),
            serializer_class='user_management.serializers.UserSerializer'
        )

        MetadataLookup(
            description=_('All the groups.'), name='groups',
            value=get_groups
        )
        MetadataLookup(
            description=_('All the users.'), name='users',
            value=get_users
        )

        SourceColumn(
            source=Group, label=_('Members'), attribute='user_set.count'
        )

        SourceColumn(
            source=User, label=_('Full name'), attribute='get_full_name'
        )
        SourceColumn(
            source=User, label=_('Email'), attribute='email'
        )
        SourceColumn(
            source=User, label=_('Active'),
            func=lambda context: two_state_template(
                context['object'].is_active
            )
        )
        SourceColumn(
            source=User, label=_('Has usable password?'),
            func=lambda context: two_state_template(
                context['object'].has_usable_password()
            )
        )

        menu_multi_item.bind_links(
            links=(link_user_multiple_set_password, link_user_multiple_delete),
            sources=('user_management:user_list',)
        )
        menu_object.bind_links(
            links=(link_group_edit, link_group_members, link_group_delete),
            sources=(Group,)
        )
        menu_object.bind_links(
            links=(
                link_user_edit, link_user_set_password, link_user_groups,
                link_user_delete
            ), sources=(User,)
        )
        menu_secondary.bind_links(
            links=(link_group_list, link_group_add), sources=(
                'user_management:group_multiple_delete',
                'user_management:group_delete', 'user_management:group_edit',
                'user_management:group_list', 'user_management:group_add',
                'user_management:group_members'
            )
        )
        menu_secondary.bind_links(
            links=(link_user_list, link_user_add), sources=(
                User, 'user_management:user_multiple_set_password',
                'user_management:user_multiple_delete',
                'user_management:user_list', 'user_management:user_add'
            )
        )
        menu_setup.bind_links(links=(link_user_setup, link_group_setup))

        registry.register(Group)
        registry.register(User)
