from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from ...classes import Permission
from ...models import StoredPermission


class Command(BaseCommand):
    help = 'Remove obsolete permissions from the database'

    def handle(self, *args, **options):
        for permission in StoredPermission.objects.all():
            try:
                Permission.get(
                    pk='{}.{}'.format(permission.namespace, permission.name),
                    proxy_only=True
                )
            except KeyError:
                permission.delete()
