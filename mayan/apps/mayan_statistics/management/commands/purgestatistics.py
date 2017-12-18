from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from ...classes import Statistic


class Command(BaseCommand):
    help = 'Remove obsolete statistics scheduled and results from the database'

    def handle(self, *args, **options):
        Statistic.purge_schedules()
