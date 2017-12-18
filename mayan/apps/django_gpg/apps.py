from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from acls import ModelPermission
from acls.links import link_acl_list
from acls.permissions import permission_acl_edit, permission_acl_view
from common import (
    MayanAppConfig, menu_facet, menu_object, menu_setup, menu_sidebar
)
from navigation import SourceColumn
from rest_api.classes import APIEndPoint

from .classes import KeyStub
from .links import (
    link_key_delete, link_key_detail, link_key_download, link_key_query,
    link_key_receive, link_key_setup, link_key_upload, link_private_keys,
    link_public_keys
)
from .licenses import *  # NOQA
from .permissions import (
    permission_key_delete, permission_key_download, permission_key_sign,
    permission_key_view
)


class DjangoGPGApp(MayanAppConfig):
    app_url = 'gpg'
    has_tests = True
    name = 'django_gpg'
    verbose_name = _('Django GPG')

    def ready(self):
        super(DjangoGPGApp, self).ready()

        APIEndPoint(app=self, version_string='1')
        Key = self.get_model('Key')

        ModelPermission.register(
            model=Key, permissions=(
                permission_acl_edit, permission_acl_view,
                permission_key_delete, permission_key_download,
                permission_key_sign, permission_key_view
            )
        )

        SourceColumn(source=Key, label=_('Key ID'), attribute='key_id')
        SourceColumn(source=Key, label=_('User ID'), attribute='user_id')

        SourceColumn(source=KeyStub, label=_('Key ID'), attribute='key_id')
        SourceColumn(source=KeyStub, label=_('Type'), attribute='key_type')
        SourceColumn(
            source=KeyStub, label=_('Creation date'), attribute='date'
        )
        SourceColumn(
            source=KeyStub, label=_('Expiration date'),
            func=lambda context: context['object'].expires or _('No expiration')
        )
        SourceColumn(source=KeyStub, label=_('Length'), attribute='length')
        SourceColumn(
            source=KeyStub, label=_('User ID'),
            func=lambda context: ', '.join(context['object'].user_id)
        )

        menu_object.bind_links(links=(link_key_detail,), sources=(Key,))
        menu_object.bind_links(links=(link_key_receive,), sources=(KeyStub,))

        menu_object.bind_links(
            links=(link_acl_list, link_key_delete, link_key_download,),
            sources=(Key,)
        )
        menu_setup.bind_links(links=(link_key_setup,))
        menu_facet.bind_links(
            links=(link_private_keys, link_public_keys),
            sources=(
                'django_gpg:key_public_list', 'django_gpg:key_private_list',
                'django_gpg:key_query', 'django_gpg:key_query_results', Key,
                KeyStub
            )
        )
        menu_sidebar.bind_links(
            links=(link_key_query, link_key_upload),
            sources=(
                'django_gpg:key_public_list', 'django_gpg:key_private_list',
                'django_gpg:key_query', 'django_gpg:key_query_results', Key,
                KeyStub
            )
        )
