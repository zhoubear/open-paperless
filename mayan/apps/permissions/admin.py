from __future__ import unicode_literals

from django.contrib import admin

from .models import StoredPermission, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    def groups_list(self, instance):
        return ','.join(instance.groups.values_list('name', flat=True))

    def permissions_list(self, instance):
        return ','.join(instance.permissions.values_list('name', flat=True))

    filter_horizontal = ('groups', 'permissions')
    list_display = ('label', 'permissions_list', 'groups_list')


@admin.register(StoredPermission)
class StoredPermissionAdmin(admin.ModelAdmin):
    list_display = ('namespace', 'name')
    list_display_links = list_display
    list_filter = ('namespace',)
