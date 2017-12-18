from django.utils.module_loading import import_string

from .settings import setting_shared_storage

shared_storage_backend = import_string(setting_shared_storage.value)()
