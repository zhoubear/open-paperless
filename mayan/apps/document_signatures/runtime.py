from django.utils.module_loading import import_string

from .settings import setting_storage_backend

storage_backend = import_string(setting_storage_backend.value)()
