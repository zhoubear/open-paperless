from __future__ import unicode_literals

from kombu import Exchange, Queue

from django.utils.translation import ugettext_lazy as _

from mayan.celery import app
from common import MayanAppConfig, menu_object, menu_secondary, menu_tools

from navigation import SourceColumn

from .classes import Statistic, StatisticNamespace
from .links import (
    link_execute, link_namespace_details, link_namespace_list,
    link_statistics, link_view
)
from .licenses import *  # NOQA
from .queues import *  # NOQA
from .tasks import task_execute_statistic  # NOQA - Force registration of task


class StatisticsApp(MayanAppConfig):
    app_namespace = 'statistics'
    has_tests = True
    name = 'mayan_statistics'
    verbose_name = _('Statistics')

    def ready(self):
        super(StatisticsApp, self).ready()

        SourceColumn(
            source=Statistic,
            # Translators: Schedule here is a verb, the 'schedule' at which the
            # statistic will be updated
            label=_('Schedule'),
            attribute='schedule',
        )

        app.conf.CELERY_QUEUES.extend(
            (
                Queue(
                    'statistics', Exchange('statistics'),
                    routing_key='statistics', delivery_mode=1
                ),
            )
        )

        app.conf.CELERY_ROUTES.update(
            {
                'mayan_statistics.tasks.task_execute_statistic': {
                    'queue': 'statistics'
                },
            }
        )

        menu_object.bind_links(
            links=(link_execute, link_view), sources=(Statistic,)
        )
        menu_object.bind_links(
            links=(link_namespace_details,), sources=(StatisticNamespace,)
        )
        menu_secondary.bind_links(
            links=(link_namespace_list,),
            sources=(StatisticNamespace, 'statistics:namespace_list')
        )
        menu_tools.bind_links(links=(link_statistics,))
