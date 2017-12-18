from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from common import MayanAppConfig, menu_tools

from .classes import APIEndPoint
from .links import link_api, link_api_documentation
from .licenses import *  # NOQA


class RESTAPIApp(MayanAppConfig):
    app_url = 'api'
    name = 'rest_api'
    verbose_name = _('REST API')

    def ready(self):
        super(RESTAPIApp, self).ready()

        settings.STRONGHOLD_PUBLIC_URLS += (r'^/%s/.+$' % self.app_url,)

        APIEndPoint(app=self, name='rest', version_string='1')

        menu_tools.bind_links(links=(link_api, link_api_documentation))
