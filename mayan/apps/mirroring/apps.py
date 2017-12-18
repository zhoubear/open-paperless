from __future__ import unicode_literals

from django import apps
from django.utils.translation import ugettext_lazy as _


class MirroringApp(apps.AppConfig):
    name = 'mirroring'
    verbose_name = _('Mirroring')
