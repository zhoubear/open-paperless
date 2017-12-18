from __future__ import absolute_import, unicode_literals

from datetime import timedelta
import logging

from kombu import Exchange, Queue

from django import apps
from django.conf import settings
from django.conf.urls import include, url
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from mayan.celery import app
from navigation.classes import Separator, Text
from rest_api.classes import APIEndPoint

from .handlers import (
    handler_pre_initial_setup, handler_pre_upgrade,
    user_locale_profile_session_config, user_locale_profile_create
)
from .links import (
    link_about, link_check_version, link_code, link_current_user_details,
    link_current_user_edit, link_current_user_locale_profile_edit,
    link_documentation, link_filters, link_forum, link_license,
    link_object_error_list_clear, link_packages_licenses, link_setup,
    link_support, link_tools
)

from .literals import DELETE_STALE_UPLOADS_INTERVAL
from .menus import (
    menu_about, menu_main, menu_secondary, menu_tools, menu_user
)
from .licenses import *  # NOQA
from .queues import *  # NOQA - Force queues registration
from .settings import setting_auto_logging, setting_production_error_log_path
from .signals import pre_initial_setup, pre_upgrade
from .tasks import task_delete_stale_uploads  # NOQA - Force task registration

logger = logging.getLogger(__name__)


class MayanAppConfig(apps.AppConfig):
    app_url = None
    app_namespace = None

    def ready(self):
        from mayan.urls import urlpatterns

        if self.app_url:
            top_url = '{}/'.format(self.app_url)
        elif self.app_url is not None:
            top_url = ''
        else:
            top_url = '{}/'.format(self.name)

        try:
            urlpatterns += url(
                r'^{}'.format(top_url),
                include(
                    '{}.urls'.format(self.name),
                    namespace=self.app_namespace or self.name
                )
            ),
        except ImportError as exception:
            if force_text(exception) not in ('No module named urls', 'No module named \'{}.urls\''.format(self.name)):
                logger.error(
                    'Import time error when running AppConfig.ready(). Check '
                    'apps.py, urls.py, views.py, etc.'
                )
                raise exception


class CommonApp(MayanAppConfig):
    app_url = ''
    has_tests = True
    name = 'common'
    verbose_name = _('Common')

    @staticmethod
    def get_user_label_text(context):
        if not context['request'].user.is_authenticated:
            return _('Anonymous')
        else:
            return context['request'].user.get_full_name() or context['request'].user

    def ready(self):
        super(CommonApp, self).ready()

        APIEndPoint(app=self, version_string='1')

        app.conf.CELERYBEAT_SCHEDULE.update(
            {
                'task_delete_stale_uploads': {
                    'task': 'common.tasks.task_delete_stale_uploads',
                    'schedule': timedelta(
                        seconds=DELETE_STALE_UPLOADS_INTERVAL
                    ),
                },
            }
        )

        app.conf.CELERY_QUEUES.extend(
            (
                Queue('default', Exchange('default'), routing_key='default'),
                Queue('tools', Exchange('tools'), routing_key='tools'),
                Queue(
                    'common_periodic', Exchange('common_periodic'),
                    routing_key='common_periodic', delivery_mode=1
                ),
            )
        )

        app.conf.CELERY_DEFAULT_QUEUE = 'default'

        app.conf.CELERY_ROUTES.update(
            {
                'common.tasks.task_delete_stale_uploads': {
                    'queue': 'common_periodic'
                },
            }
        )
        menu_user.bind_links(
            links=(
                Text(text=CommonApp.get_user_label_text), Separator(),
                link_current_user_details, link_current_user_edit,
                link_current_user_locale_profile_edit,
                Separator()
            )
        )

        menu_about.bind_links(
            links=(
                link_tools, link_setup, link_about,# link_support,
                #link_documentation, link_forum, link_code,
                link_license, link_packages_licenses#, link_check_version
            )
        )

        menu_main.bind_links(links=(menu_about, menu_user,), position=99)
        menu_secondary.bind_links(
            links=(link_object_error_list_clear,), sources=(
                'common:object_error_list',
            )
        )
        #menu_tools.bind_links(
        #    links=(link_filters,)
        #)

        post_save.connect(
            user_locale_profile_create,
            dispatch_uid='user_locale_profile_create',
            sender=settings.AUTH_USER_MODEL
        )
        pre_initial_setup.connect(
            handler_pre_initial_setup,
            dispatch_uid='common_handler_pre_initial_setup'
        )
        pre_upgrade.connect(
            handler_pre_upgrade,
            dispatch_uid='common_handler_pre_upgrade',
        )

        user_logged_in.connect(
            user_locale_profile_session_config,
            dispatch_uid='user_locale_profile_session_config'
        )
        self.setup_auto_logging()

    def setup_auto_logging(self):
        if setting_auto_logging.value:
            if settings.DEBUG:
                level = 'DEBUG'
                handlers = ['console']
            else:
                level = 'ERROR'
                handlers = ['console', 'logfile']

            loggers = {}
            for project_app in apps.apps.get_app_configs():
                loggers[project_app.name] = {
                    'handlers': handlers,
                    'propagate': True,
                    'level': level,
                }

            logging.config.dictConfig(
                {
                    'version': 1,
                    'disable_existing_loggers': True,
                    'formatters': {
                        'intermediate': {
                            'format': '%(name)s <%(process)d> [%(levelname)s] "%(funcName)s() line %(lineno)d %(message)s"'
                        },
                        'logfile': {
                            'format': '%(asctime)s %(name)s <%(process)d> [%(levelname)s] "%(funcName)s() line %(lineno)d %(message)s"'
                        },
                    },
                    'handlers': {
                        'console': {
                            'class': 'logging.StreamHandler',
                            'formatter': 'intermediate',
                            'level': 'DEBUG',
                        },
                        'logfile': {
                            'class': 'logging.handlers.WatchedFileHandler',
                            'filename': setting_production_error_log_path.value,
                            'formatter': 'logfile'
                        },
                    },
                    'loggers': loggers
                }
            )
