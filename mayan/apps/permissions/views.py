from __future__ import unicode_literals

import itertools

from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from common.views import (
    AssignRemoveView, SingleObjectCreateView, SingleObjectDeleteView,
    SingleObjectEditView, SingleObjectListView
)

from .classes import Permission, PermissionNamespace
from .models import Role, StoredPermission
from .permissions import (
    permission_permission_grant, permission_permission_revoke,
    permission_role_view, permission_role_create, permission_role_delete,
    permission_role_edit
)


class RoleCreateView(SingleObjectCreateView):
    fields = ('label',)
    model = Role
    view_permission = permission_role_create
    post_action_redirect = reverse_lazy('permissions:role_list')


class RoleDeleteView(SingleObjectDeleteView):
    model = Role
    view_permission = permission_role_delete
    post_action_redirect = reverse_lazy('permissions:role_list')


class RoleEditView(SingleObjectEditView):
    fields = ('label',)
    model = Role
    view_permission = permission_role_edit


class SetupRoleMembersView(AssignRemoveView):
    grouped = False
    left_list_title = _('Available groups')
    right_list_title = _('Role groups')
    view_permission = permission_role_edit

    def add(self, item):
        group = get_object_or_404(Group, pk=item)
        self.get_object().groups.add(group)

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Groups of role: %s') % self.get_object()
        }

    def get_object(self):
        return get_object_or_404(Role, pk=self.kwargs['pk'])

    def left_list(self):
        return [
            (force_text(group.pk), group.name) for group in set(Group.objects.all()) - set(self.get_object().groups.all())
        ]

    def right_list(self):
        return [
            (force_text(group.pk), group.name) for group in self.get_object().groups.all()
        ]

    def remove(self, item):
        group = get_object_or_404(Group, pk=item)
        self.get_object().groups.remove(group)


class SetupRolePermissionsView(AssignRemoveView):
    grouped = True
    left_list_title = _('Available permissions')
    right_list_title = _('Granted permissions')
    view_permission = permission_role_view

    def add(self, item):
        Permission.check_permissions(
            self.request.user, permissions=(permission_permission_grant,)
        )
        permission = get_object_or_404(StoredPermission, pk=item)
        self.get_object().permissions.add(permission)

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Permissions for role: %s') % self.get_object(),
        }

    def get_object(self):
        return get_object_or_404(Role, pk=self.kwargs['pk'])

    def left_list(self):
        Permission.refresh()
        results = []

        for namespace, permissions in itertools.groupby(StoredPermission.objects.exclude(id__in=self.get_object().permissions.values_list('pk', flat=True)), lambda entry: entry.namespace):
            permission_options = [
                (force_text(permission.pk), permission) for permission in permissions
            ]
            results.append(
                (PermissionNamespace.get(namespace), permission_options)
            )

        return results

    def right_list(self):
        results = []
        for namespace, permissions in itertools.groupby(self.get_object().permissions.all(), lambda entry: entry.namespace):
            permission_options = [
                (force_text(permission.pk), permission) for permission in permissions
            ]
            results.append(
                (PermissionNamespace.get(namespace), permission_options)
            )

        return results

    def remove(self, item):
        Permission.check_permissions(
            self.request.user, permissions=(permission_permission_revoke,)
        )
        permission = get_object_or_404(StoredPermission, pk=item)
        self.get_object().permissions.remove(permission)


class RoleListView(SingleObjectListView):
    extra_context = {
        'hide_link': True,
        'title': _('Roles'),
    }

    model = Role
    view_permission = permission_role_view
