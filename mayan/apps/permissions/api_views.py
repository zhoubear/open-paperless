from __future__ import unicode_literals

from rest_framework import generics

from rest_api.filters import MayanObjectPermissionsFilter
from rest_api.permissions import MayanPermission

from .classes import Permission
from .models import Role
from .permissions import (
    permission_role_create, permission_role_delete, permission_role_edit,
    permission_role_view
)
from .serializers import (
    PermissionSerializer, RoleSerializer, WritableRoleSerializer
)


class APIPermissionList(generics.ListAPIView):
    serializer_class = PermissionSerializer
    queryset = Permission.all()

    def get(self, *args, **kwargs):
        """
        Returns a list of all the available permissions.
        """

        return super(APIPermissionList, self).get(*args, **kwargs)


class APIRoleListView(generics.ListCreateAPIView):
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_role_view,)}
    mayan_view_permissions = {'POST': (permission_role_create,)}
    permission_classes = (MayanPermission,)
    queryset = Role.objects.all()

    def get(self, *args, **kwargs):
        """
        Returns a list of all the roles.
        """

        return super(APIRoleListView, self).get(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RoleSerializer
        elif self.request.method == 'POST':
            return WritableRoleSerializer

    def post(self, *args, **kwargs):
        """
        Create a new role.
        """

        return super(APIRoleListView, self).post(*args, **kwargs)


class APIRoleView(generics.RetrieveUpdateDestroyAPIView):
    mayan_object_permissions = {
        'GET': (permission_role_view,),
        'PUT': (permission_role_edit,),
        'PATCH': (permission_role_edit,),
        'DELETE': (permission_role_delete,)
    }
    permission_classes = (MayanPermission,)
    queryset = Role.objects.all()

    def delete(self, *args, **kwargs):
        """
        Delete the selected role.
        """

        return super(APIRoleView, self).delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Return the details of the selected role.
        """

        return super(APIRoleView, self).get(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RoleSerializer
        elif self.request.method in ('PATCH', 'PUT'):
            return WritableRoleSerializer

    def patch(self, *args, **kwargs):
        """
        Edit the selected role.
        """

        return super(APIRoleView, self).patch(*args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Edit the selected role.
        """

        return super(APIRoleView, self).put(*args, **kwargs)
