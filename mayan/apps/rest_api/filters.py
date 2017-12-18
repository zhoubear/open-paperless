from __future__ import absolute_import, unicode_literals

from rest_framework.filters import BaseFilterBackend

from acls.models import AccessControlList


class MayanObjectPermissionsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        # TODO: fix variable name to make it clear it should be a single
        # permission

        required_permissions = getattr(
            view, 'mayan_object_permissions', {}
        ).get(request.method, None)

        if required_permissions:
            return AccessControlList.objects.filter_by_access(
                required_permissions[0], request.user, queryset=queryset
            )
        else:
            return queryset
