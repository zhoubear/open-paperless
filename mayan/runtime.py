from django.utils.module_loading import import_string

from .conf import setting_celery_class

celery_class = import_string(setting_celery_class.value)
