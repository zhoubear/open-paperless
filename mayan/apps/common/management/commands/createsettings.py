from __future__ import unicode_literals

import os

from django.conf import settings
from django.core import management
from django.core.management.utils import get_random_secret_key

from ...settings import setting_local_settings_filename

from .literals import SETTING_FILE_TEMPLATE


class Command(management.BaseCommand):
    help = 'Creates a local settings file with a random secret key.'

    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, 'settings', '{}.py'.format(setting_local_settings_filename.value))
        if os.path.exists(path):
            self.stdout.write(self.style.NOTICE('Existing settings file at: {0}. Backup, remove this file, and try again.'.format(path)))
        else:
            with open(path, 'w+') as file_object:
                file_object.write(
                    SETTING_FILE_TEMPLATE.format(get_random_secret_key())
                )
