from django.utils.module_loading import import_string

from .settings import setting_cache_storage_backend, setting_storage_backend

storage_backend = import_string(setting_storage_backend.value)()
cache_storage_backend = import_string(setting_cache_storage_backend.value)()
