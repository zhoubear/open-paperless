from __future__ import unicode_literals

from django import apps
from django.utils.translation import ugettext_lazy as _


class LockManagerApp(apps.AppConfig):
    has_tests = True
    name = 'lock_manager'
    verbose_name = _('Lock manager')
