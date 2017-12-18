from __future__ import unicode_literals

from django.conf.urls import url

from .views import APIBase, APIAppView, BrowseableObtainAuthToken


urlpatterns = [
]

api_urls = [
    url(r'^$', APIBase.as_view(), name='api_root'),
    url(r'^api/(?P<path>.*)/?$', APIAppView.as_view(), name='api_app'),
    url(
        r'^auth/token/obtain/$', BrowseableObtainAuthToken.as_view(),
        name='auth_token_obtain'
    ),
]
