from __future__ import unicode_literals

import os

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from smart_settings import Namespace

namespace = Namespace(name='storage', label=_('Storage'))
setting_filestorage_location = namespace.add_setting(
    global_name='STORAGE_FILESTORAGE_LOCATION',
    default=os.path.join(settings.MEDIA_ROOT, 'document_storage'), is_path=True
)
