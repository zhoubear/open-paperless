from __future__ import unicode_literals

from django.core import management

from ...signals import post_initial_setup, pre_initial_setup


class Command(management.BaseCommand):
    help = 'Initializes an install and gets it ready to be used.'

    def handle(self, *args, **options):
        management.call_command('createsettings', interactive=False)
        pre_initial_setup.send(sender=self)
        management.call_command('createautoadmin', interactive=False)
        post_initial_setup.send(sender=self)
