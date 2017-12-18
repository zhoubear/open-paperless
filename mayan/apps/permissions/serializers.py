from __future__ import unicode_literals

from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from user_management.serializers import GroupSerializer

from .classes import Permission
from .models import Role, StoredPermission


class PermissionSerializer(serializers.Serializer):
    namespace = serializers.CharField(read_only=True)
    pk = serializers.CharField(read_only=True)
    label = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        if isinstance(instance, StoredPermission):
            return super(PermissionSerializer, self).to_representation(
                instance.volatile_permission
            )
        else:
            return super(PermissionSerializer, self).to_representation(
                instance
            )


class RoleSerializer(serializers.HyperlinkedModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        extra_kwargs = {
            'url': {'view_name': 'rest_api:role-detail'},
        }
        fields = ('groups', 'id', 'label', 'permissions', 'url')
        model = Role


class WritableRoleSerializer(serializers.HyperlinkedModelSerializer):
    groups_pk_list = serializers.CharField(
        help_text=_(
            'Comma separated list of groups primary keys to add to, or replace'
            ' in this role.'
        ), required=False
    )

    permissions_pk_list = serializers.CharField(
        help_text=_(
            'Comma separated list of permission primary keys to grant to this '
            'role.'
        ), required=False
    )

    class Meta:
        fields = ('groups_pk_list', 'id', 'label', 'permissions_pk_list')
        model = Role

    def create(self, validated_data):
        self.groups_pk_list = validated_data.pop('groups_pk_list', '')
        self.permissions_pk_list = validated_data.pop(
            'permissions_pk_list', ''
        )

        instance = super(WritableRoleSerializer, self).create(validated_data)

        if self.groups_pk_list:
            self._add_groups(instance=instance)

        if self.permissions_pk_list:
            self._add_permissions(instance=instance)

        return instance

    def _add_groups(self, instance):
        instance.groups.add(
            *Group.objects.filter(pk__in=self.groups_pk_list.split(','))
        )

    def _add_permissions(self, instance):
        for pk in self.permissions_pk_list.split(','):
            try:
                stored_permission = Permission.get(pk=pk)
                instance.permissions.add(stored_permission)
                instance.save()
            except KeyError:
                raise ValidationError(_('No such permission: %s') % pk)

    def update(self, instance, validated_data):
        result = validated_data.copy()

        self.groups_pk_list = validated_data.pop('groups_pk_list', '')
        self.permissions_pk_list = validated_data.pop(
            'permissions_pk_list', ''
        )

        result = super(WritableRoleSerializer, self).update(
            instance, validated_data
        )

        if self.groups_pk_list:
            instance.groups.clear()
            self._add_groups(instance=instance)

        if self.permissions_pk_list:
            instance.permissions.clear()
            self._add_permissions(instance=instance)

        return result
