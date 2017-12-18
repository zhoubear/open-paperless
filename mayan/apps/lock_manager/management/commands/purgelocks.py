from __future__ import unicode_literals

from django.core import management

from ...runtime import locking_backend


class Command(management.BaseCommand):
    help = 'Erase all locks (acquired and stale).'

    def handle(self, *args, **options):
        locking_backend.purge_locks()
