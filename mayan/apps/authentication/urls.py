from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.views import logout

from .views import (
    login_view, password_change_done, password_change_view,
    password_reset_complete_view, password_reset_confirm_view,
    password_reset_done_view, password_reset_view
)


urlpatterns = [
    url(r'^login/$', login_view, name='login_view'),
    url(
        r'^password/change/done/$', password_change_done,
        name='password_change_done'
    ),
    url(
        r'^password/change/$', password_change_view,
        name='password_change_view'
    ),
    url(
        r'^logout/$', logout, {'next_page': settings.LOGIN_REDIRECT_URL},
        name='logout_view'
    ),
    url(
        r'^password/reset/$', password_reset_view, name='password_reset_view'
    ),
    url(
        r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        password_reset_confirm_view, name='password_reset_confirm_view'
    ),
    url(
        r'^password/reset/complete/$', password_reset_complete_view,
        name='password_reset_complete_view'
    ),
    url(
        r'^password/reset/done/$', password_reset_done_view,
        name='password_reset_done_view'
    ),
]
