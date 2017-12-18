from __future__ import absolute_import

from __future__ import unicode_literals

from django.core.exceptions import PermissionDenied

from rest_framework.permissions import BasePermission

from acls.models import AccessControlList
from permissions import Permission


class MayanPermission(BasePermission):
    def has_permission(self, request, view):
        required_permission = getattr(
            view, 'mayan_view_permissions', {}
        ).get(request.method, None)

        if required_permission:
            try:
                Permission.check_permissions(request.user, required_permission)
            except PermissionDenied:
                return False
            else:
                return True
        else:
            return True

    def has_object_permission(self, request, view, obj):
        required_permission = getattr(
            view, 'mayan_object_permissions', {}
        ).get(request.method, None)

        if required_permission:
            try:
                if hasattr(view, 'mayan_permission_attribute_check'):
                    AccessControlList.objects.check_access(
                        permissions=required_permission,
                        user=request.user, obj=obj,
                        related=view.mayan_permission_attribute_check
                    )
                else:
                    AccessControlList.objects.check_access(
                        permissions=required_permission, user=request.user,
                        obj=obj
                    )
            except PermissionDenied:
                return False
            else:
                return True
        else:
            return True
