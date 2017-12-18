from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from common import MayanAppConfig

from .licenses import *  # NOQA


class MIMETypesApp(MayanAppConfig):
    name = 'mimetype'
    verbose_name = _('MIME types')

    def ready(self, *args, **kwargs):
        super(MIMETypesApp, self).ready(*args, **kwargs)
