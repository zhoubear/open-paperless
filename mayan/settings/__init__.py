from __future__ import absolute_import

from django.utils.encoding import force_text

try:
    from .local import *  # NOQA
except ImportError as exception:
    if force_text(exception) != 'No module named local' and force_text(exception) != 'No module named \'mayan.settings.local\'':
        raise
    from .base import *  # NOQA
