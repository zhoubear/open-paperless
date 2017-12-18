from django.utils.module_loading import import_string

from .settings import setting_ocr_backend

ocr_backend = import_string(setting_ocr_backend.value)()
