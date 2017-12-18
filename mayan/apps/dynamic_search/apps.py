from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from common import MayanAppConfig, menu_facet, menu_sidebar
from rest_api.classes import APIEndPoint

from .links import link_search, link_search_advanced, link_search_again


class DynamicSearchApp(MayanAppConfig):
    app_namespace = 'search'
    app_url = 'search'
    has_tests = True
    name = 'dynamic_search'
    verbose_name = _('Dynamic search')

    def ready(self):
        super(DynamicSearchApp, self).ready()

        APIEndPoint(app=self, version_string='1')

        menu_facet.bind_links(
            links=(link_search, link_search_advanced),
            sources=(
                'search:search', 'search:search_advanced', 'search:results'
            )
        )
        menu_sidebar.bind_links(
            links=(link_search_again,), sources=('search:results',)
        )
