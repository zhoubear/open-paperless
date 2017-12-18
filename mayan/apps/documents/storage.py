from __future__ import unicode_literals

import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .literals import CACHE_PATH


class LocalCacheFileStorage(FileSystemStorage):
    """Simple wrapper for the stock Django FileSystemStorage class"""

    def __init__(self, *args, **kwargs):
        super(LocalCacheFileStorage, self).__init__(*args, **kwargs)
        self.location = os.path.join(settings.MEDIA_ROOT, CACHE_PATH)
        if not os.path.exists(os.path.dirname(self.location)):
            os.makedirs(os.path.dirname(self.location))
