from __future__ import unicode_literals

import os

from django.core.files.storage import FileSystemStorage

from ..settings import setting_filestorage_location


class FileBasedStorage(FileSystemStorage):
    """Simple wrapper for the stock Django FileSystemStorage class"""

    separator = os.path.sep

    def __init__(self, *args, **kwargs):
        super(FileBasedStorage, self).__init__(*args, **kwargs)
        self.location = setting_filestorage_location.value
