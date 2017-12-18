from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Link

link_search = Link(
    text=_('Search'), view='search:search', args='search_model.get_full_name'
)
link_search_advanced = Link(
    text=_('Advanced search'), view='search:search_advanced',
    args='search_model.get_full_name'
)
link_search_again = Link(
    text=_('Search again'), view='search:search_again',
    args='search_model.get_full_name', keep_query=True
)
