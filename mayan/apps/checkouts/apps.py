from __future__ import absolute_import, unicode_literals

from datetime import timedelta

from kombu import Exchange, Queue

from django.apps import apps
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _

from acls import ModelPermission
from common import MayanAppConfig, menu_facet, menu_main, menu_sidebar
from common.dashboards import dashboard_main
from mayan.celery import app
from rest_api.classes import APIEndPoint

from .dashboard_widgets import widget_checkouts
from .handlers import check_new_version_creation
from .links import (
    link_checkin_document, link_checkout_document, link_checkout_info,
    link_checkout_list
)
from .literals import CHECK_EXPIRED_CHECK_OUTS_INTERVAL
from .permissions import (
    permission_document_checkin, permission_document_checkin_override,
    permission_document_checkout, permission_document_checkout_detail_view
)
from .queues import *  # NOQA
from .tasks import task_check_expired_check_outs  # NOQA
# This import is required so that celerybeat can find the task


class CheckoutsApp(MayanAppConfig):
    has_tests = True
    name = 'checkouts'
    verbose_name = _('Checkouts')

    def ready(self):
        super(CheckoutsApp, self).ready()

        APIEndPoint(app=self, version_string='1')

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )
        DocumentVersion = apps.get_model(
            app_label='documents', model_name='DocumentVersion'
        )

        DocumentCheckout = self.get_model('DocumentCheckout')

        Document.add_to_class(
            'check_in',
            lambda document, user=None: DocumentCheckout.objects.check_in_document(document, user)
        )
        Document.add_to_class(
            'checkout_info',
            lambda document: DocumentCheckout.objects.document_checkout_info(
                document
            )
        )
        Document.add_to_class(
            'checkout_state',
            lambda document: DocumentCheckout.objects.document_checkout_state(
                document
            )
        )
        Document.add_to_class(
            'is_checked_out',
            lambda document: DocumentCheckout.objects.is_document_checked_out(
                document
            )
        )

        ModelPermission.register(
            model=Document, permissions=(
                permission_document_checkout,
                permission_document_checkin,
                permission_document_checkin_override,
                permission_document_checkout_detail_view
            )
        )

        app.conf.CELERYBEAT_SCHEDULE.update(
            {
                'task_check_expired_check_outs': {
                    'task': 'checkouts.tasks.task_check_expired_check_outs',
                    'schedule': timedelta(
                        seconds=CHECK_EXPIRED_CHECK_OUTS_INTERVAL
                    ),
                },
            }
        )

        app.conf.CELERY_QUEUES.append(
            Queue(
                'checkouts_periodic', Exchange('checkouts_periodic'),
                routing_key='checkouts_periodic', delivery_mode=1
            ),
        )

        app.conf.CELERY_ROUTES.update(
            {
                'checkouts.tasks.task_check_expired_check_outs': {
                    'queue': 'checkouts_periodic'
                },
            }
        )

        dashboard_main.add_widget(order=-1, widget=widget_checkouts)

        menu_facet.bind_links(links=(link_checkout_info,), sources=(Document,))
        menu_main.bind_links(links=(link_checkout_list,), position=98)
        menu_sidebar.bind_links(
            links=(link_checkout_document, link_checkin_document),
            sources=(
                'checkouts:checkout_info', 'checkouts:checkout_document',
                'checkouts:checkin_document'
            )
        )

        pre_save.connect(
            check_new_version_creation,
            dispatch_uid='check_new_version_creation',
            sender=DocumentVersion
        )
