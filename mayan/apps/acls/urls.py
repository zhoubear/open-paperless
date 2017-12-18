from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIObjectACLListView, APIObjectACLPermissionListView,
    APIObjectACLPermissionView, APIObjectACLView
)
from .views import (
    ACLCreateView, ACLDeleteView, ACLListView, ACLPermissionsView
)

urlpatterns = [
    url(
        r'^(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_id>\d+)/create/$',
        ACLCreateView.as_view(), name='acl_create'
    ),
    url(
        r'^(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_id>\d+)/list/$',
        ACLListView.as_view(), name='acl_list'
    ),
    url(r'^(?P<pk>\d+)/delete/$', ACLDeleteView.as_view(), name='acl_delete'),
    url(
        r'^(?P<pk>\d+)/permissions/$', ACLPermissionsView.as_view(),
        name='acl_permissions'
    ),
]

api_urls = [
    url(
        r'^object/(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_pk>\d+)/acls/$',
        APIObjectACLListView.as_view(), name='accesscontrollist-list'
    ),
    url(
        r'^object/(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_pk>\d+)/acls/(?P<pk>\d+)/$',
        APIObjectACLView.as_view(), name='accesscontrollist-detail'
    ),
    url(
        r'^object/(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_pk>\d+)/acls/(?P<pk>\d+)/permissions/$',
        APIObjectACLPermissionListView.as_view(), name='accesscontrollist-permission-list'
    ),
    url(
        r'^object/(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_pk>\d+)/acls/(?P<pk>\d+)/permissions/(?P<permission_pk>\d+)/$',
        APIObjectACLPermissionView.as_view(), name='accesscontrollist-permission-detail'
    ),
]
