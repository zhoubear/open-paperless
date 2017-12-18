from __future__ import unicode_literals

from kombu import Exchange, Queue

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from acls import ModelPermission
from acls.links import link_acl_list
from acls.permissions import permission_acl_edit, permission_acl_view
from common import (
    MayanAppConfig, menu_object, menu_multi_item, menu_secondary, menu_setup,
    menu_tools
)
from common.widgets import two_state_template
from mayan.celery import app
from navigation import SourceColumn

from .classes import MailerBackend
from .links import (
    link_send_document_link, link_send_document, link_send_multiple_document,
    link_send_multiple_document_link, link_system_mailer_error_log,
    link_user_mailer_create, link_user_mailer_delete, link_user_mailer_edit,
    link_user_mailer_list, link_user_mailer_log_list, link_user_mailer_setup,
    link_user_mailer_test
)
from .permissions import (
    permission_mailing_link, permission_mailing_send_document,
    permission_user_mailer_delete, permission_user_mailer_edit,
    permission_user_mailer_use, permission_user_mailer_view,
)
from .queues import *  # NOQA


class MailerApp(MayanAppConfig):
    has_tests = True
    name = 'mailer'
    verbose_name = _('Mailer')

    def ready(self):
        super(MailerApp, self).ready()

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )

        LogEntry = self.get_model('LogEntry')
        UserMailer = self.get_model('UserMailer')

        MailerBackend.initialize()

        SourceColumn(
            source=LogEntry, label=_('Date and time'), attribute='datetime'
        )
        SourceColumn(
            source=LogEntry, label=_('Message'), attribute='message'
        )
        SourceColumn(
            source=UserMailer, label=_('Label'), attribute='label'
        )
        SourceColumn(
            source=UserMailer, label=_('Default?'),
            func=lambda context: two_state_template(
                context['object'].default
            )
        )
        SourceColumn(
            source=UserMailer, label=_('Enabled?'),
            func=lambda context: two_state_template(
                context['object'].enabled
            )
        )
        SourceColumn(
            source=UserMailer, label=_('Label'), attribute='backend_label'
        )

        ModelPermission.register(
            model=Document, permissions=(
                permission_mailing_link, permission_mailing_send_document
            )
        )

        ModelPermission.register(
            model=UserMailer, permissions=(
                permission_acl_edit, permission_acl_view,
                permission_user_mailer_delete, permission_user_mailer_edit,
                permission_user_mailer_view, permission_user_mailer_use
            )
        )

        app.conf.CELERY_QUEUES.append(
            Queue('mailing', Exchange('mailing'), routing_key='mailing'),
        )

        app.conf.CELERY_ROUTES.update(
            {
                'mailer.tasks.task_send_document': {
                    'queue': 'mailing'
                },
            }
        )

        menu_multi_item.bind_links(
            links=(
                link_send_multiple_document, link_send_multiple_document_link
            ), sources=(Document,)
        )

        menu_object.bind_links(
            links=(
                link_send_document_link, link_send_document
            ), sources=(Document,)
        )

        menu_object.bind_links(
            links=(
                link_user_mailer_edit, link_user_mailer_log_list,
                link_user_mailer_test, link_acl_list, link_user_mailer_delete,
            ), sources=(UserMailer,)
        )

        menu_secondary.bind_links(
            links=(
                link_user_mailer_list, link_user_mailer_create,
            ), sources=(
                UserMailer, 'mailer:user_mailer_list',
                'mailer:user_mailer_create'
            )
        )

        menu_tools.bind_links(links=(link_system_mailer_error_log,))

        menu_setup.bind_links(links=(link_user_mailer_setup,))
