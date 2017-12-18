from __future__ import unicode_literals

import logging

from django.utils.module_loading import import_string

from .settings import setting_graphics_backend

logger = logging.getLogger(__name__)
backend = converter_class = import_string(setting_graphics_backend.value)
