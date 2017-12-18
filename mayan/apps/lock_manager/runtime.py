from django.utils.module_loading import import_string

from .settings import setting_backend

locking_backend = import_string(setting_backend.value)
