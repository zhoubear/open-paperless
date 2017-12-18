from __future__ import unicode_literals

from django.core import management


def purge_permissions(**kwargs):
    management.call_command('purgepermissions')
