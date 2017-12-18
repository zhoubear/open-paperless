from __future__ import absolute_import, unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from common.serializers import ContentTypeSerializer
from permissions import Permission
from permissions.models import Role, StoredPermission
from permissions.serializers import PermissionSerializer, RoleSerializer

from .models import AccessControlList


class AccessControlListSerializer(serializers.ModelSerializer):
    content_type = ContentTypeSerializer(read_only=True)
    permissions_url = serializers.SerializerMethodField(
        help_text=_(
            'API URL pointing to the list of permissions for this access '
            'control list.'
        )
    )
    role = RoleSerializer(read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'content_type', 'id', 'object_id', 'permissions_url', 'role', 'url'
        )
        model = AccessControlList

    def get_permissions_url(self, instance):
        return reverse(
            'rest_api:accesscontrollist-permission-list', args=(
                instance.content_type.app_label, instance.content_type.model,
                instance.object_id, instance.pk
            ), request=self.context['request'], format=self.context['format']
        )

    def get_url(self, instance):
        return reverse(
            'rest_api:accesscontrollist-detail', args=(
                instance.content_type.app_label, instance.content_type.model,
                instance.object_id, instance.pk
            ), request=self.context['request'], format=self.context['format']
        )


class AccessControlListPermissionSerializer(PermissionSerializer):
    acl_permission_url = serializers.SerializerMethodField(
        help_text=_(
            'API URL pointing to a permission in relation to the '
            'access control list to which it is attached. This URL is '
            'different than the canonical workflow URL.'
        )
    )
    acl_url = serializers.SerializerMethodField()

    def get_acl_permission_url(self, instance):
        return reverse(
            'rest_api:accesscontrollist-permission-detail', args=(
                self.context['acl'].content_type.app_label,
                self.context['acl'].content_type.model,
                self.context['acl'].object_id, self.context['acl'].pk,
                instance.stored_permission.pk
            ), request=self.context['request'], format=self.context['format']
        )

    def get_acl_url(self, instance):
        return reverse(
            'rest_api:accesscontrollist-detail', args=(
                self.context['acl'].content_type.app_label,
                self.context['acl'].content_type.model,
                self.context['acl'].object_id, self.context['acl'].pk
            ), request=self.context['request'], format=self.context['format']
        )


class WritableAccessControlListPermissionSerializer(AccessControlListPermissionSerializer):
    permission_pk = serializers.CharField(
        help_text=_(
            'Primary key of the new permission to grant to the access control '
            'list.'
        ), write_only=True
    )

    class Meta:
        fields = ('namespace',)
        read_only_fields = ('namespace',)

    def create(self, validated_data):
        for permission in validated_data['permissions']:
            self.context['acl'].permissions.add(permission)

        return validated_data['permissions'][0]

    def validate(self, attrs):
        permissions_pk_list = attrs.pop('permission_pk', None)
        permissions_result = []

        if permissions_pk_list:
            for pk in permissions_pk_list.split(','):
                try:
                    permission = Permission.get(pk=pk)
                except KeyError:
                    raise ValidationError(_('No such permission: %s') % pk)
                else:
                    # Accumulate valid stored permission pks
                    permissions_result.append(permission.pk)

        attrs['permissions'] = StoredPermission.objects.filter(
            pk__in=permissions_result
        )
        return attrs


class WritableAccessControlListSerializer(serializers.ModelSerializer):
    content_type = ContentTypeSerializer(read_only=True)
    permissions_pk_list = serializers.CharField(
        help_text=_(
            'Comma separated list of permission primary keys to grant to this '
            'access control list.'
        ), required=False
    )
    permissions_url = serializers.SerializerMethodField(
        help_text=_(
            'API URL pointing to the list of permissions for this access '
            'control list.'
        ), read_only=True
    )
    role_pk = serializers.IntegerField(
        help_text=_(
            'Primary keys of the role to which this access control list '
            'binds to.'
        ), write_only=True
    )
    url = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'content_type', 'id', 'object_id', 'permissions_pk_list',
            'permissions_url', 'role_pk', 'url'
        )
        model = AccessControlList
        read_only_fields = ('content_type', 'object_id')

    def get_permissions_url(self, instance):
        return reverse(
            'rest_api:accesscontrollist-permission-list', args=(
                instance.content_type.app_label, instance.content_type.model,
                instance.object_id, instance.pk
            ), request=self.context['request'], format=self.context['format']
        )

    def get_url(self, instance):
        return reverse(
            'rest_api:accesscontrollist-detail', args=(
                instance.content_type.app_label, instance.content_type.model,
                instance.object_id, instance.pk
            ), request=self.context['request'], format=self.context['format']
        )

    def validate(self, attrs):
        attrs['content_type'] = ContentType.objects.get_for_model(
            self.context['content_object']
        )
        attrs['object_id'] = self.context['content_object'].pk

        try:
            attrs['role'] = Role.objects.get(pk=attrs.pop('role_pk'))
        except Role.DoesNotExist as exception:
            raise ValidationError(force_text(exception))

        permissions_pk_list = attrs.pop('permissions_pk_list', None)
        permissions_result = []

        if permissions_pk_list:
            for pk in permissions_pk_list.split(','):
                try:
                    permission = Permission.get(pk=pk)
                except KeyError:
                    raise ValidationError(_('No such permission: %s') % pk)
                else:
                    # Accumulate valid stored permission pks
                    permissions_result.append(permission.pk)

        instance = AccessControlList(**attrs)

        try:
            instance.full_clean()
        except DjangoValidationError as exception:
            raise ValidationError(exception)

        # Add a queryset of valid stored permissions so that they get added
        # after the ACL gets created.
        attrs['permissions'] = StoredPermission.objects.filter(
            pk__in=permissions_result
        )
        return attrs
