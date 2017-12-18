from __future__ import unicode_literals

from django import apps
from django.test.runner import DiscoverRunner


class MayanTestRunner(DiscoverRunner):
    @classmethod
    def add_arguments(cls, parser):
        DiscoverRunner.add_arguments(parser)
        parser.add_argument(
            '--mayan-apps', action='store_true', default=False,
            dest='mayan_apps',
            help='Test all Mayan apps that report to have tests.'
        )

    def __init__(self, *args, **kwargs):
        self.mayan_apps = kwargs.pop('mayan_apps')
        super(MayanTestRunner, self).__init__(*args, **kwargs)

    def build_suite(self, *args, **kwargs):
        # Apps that report they have tests
        if self.mayan_apps:
            args = list(args)
            args[0] = [
                app.name for app in apps.apps.get_app_configs() if getattr(
                    app, 'has_tests', False
                )
            ]

        return super(MayanTestRunner, self).build_suite(*args, **kwargs)
