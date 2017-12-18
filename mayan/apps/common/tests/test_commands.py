from __future__ import unicode_literals

import os
import uuid

from django.core import management
from django.conf import settings
from django.utils.encoding import force_text

from ..utils import fs_cleanup
from ..management.commands.literals import SETTING_FILE_TEMPLATE

from .base import BaseTestCase


class CommonCommandsTestCase(BaseTestCase):
    def test_createsettings_command(self):
        filename = force_text(uuid.uuid4())
        with self.settings(COMMON_LOCAL_SETTINGS_FILENAME=filename):
            management.call_command('createsettings', interactive=False)
            file_path = os.path.join(
                settings.BASE_DIR, 'settings', '{}.py'.format(filename)
            )

            with open(file_path) as file_object:
                content = file_object.read()

        fs_cleanup(filename=file_path)
        # Compare without the string substitution and the final linefeeds
        self.assertTrue(
            SETTING_FILE_TEMPLATE.replace("{0}'", '')[0:-2] in content
        )
