from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIAdvancedSearchView, APISearchModelList, APISearchView
)
from .views import (
    AdvancedSearchView, ResultsView, SearchAgainView, SearchView
)

urlpatterns = [
    url(r'^(?P<search_model>[\.\w]+)/$', SearchView.as_view(), name='search'),
    url(
        r'^advanced/(?P<search_model>[\.\w]+)/$', AdvancedSearchView.as_view(),
        name='search_advanced'
    ),
    url(
        r'^again/(?P<search_model>[\.\w]+)/$', SearchAgainView.as_view(),
        name='search_again'
    ),
    url(
        r'^results/(?P<search_model>[\.\w]+)/$', ResultsView.as_view(),
        name='results'
    ),
]

api_urls = [
    url(
        r'^search_models/$', APISearchModelList.as_view(),
        name='searchmodel-list'
    ),
    url(
        r'^search/(?P<search_model>[\.\w]+)/$', APISearchView.as_view(),
        name='search-view'
    ),
    url(
        r'^advanced/(?P<search_model>[\.\w]+)/$', APIAdvancedSearchView.as_view(),
        name='advanced-search-view'
    ),
]
