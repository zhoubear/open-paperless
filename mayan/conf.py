"""
This module should be called settings.py but is named conf.py to avoid a
class with the mayan/settings/* module
"""

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from smart_settings import Namespace

namespace = Namespace(name='mayan', label=_('Mayan'))

setting_celery_class = namespace.add_setting(
    help_text=_('The class used to instanciate the main Celery app.'),
    global_name='MAYAN_CELERY_CLASS',
    default='celery.Celery'
)
