from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    users_count = serializers.SerializerMethodField()

    class Meta:
        extra_kwargs = {
            'url': {'view_name': 'rest_api:group-detail'}
        }
        fields = ('id', 'name', 'url', 'users_count')
        model = Group

    def get_users_count(self, instance):
        return instance.user_set.count()


class UserGroupListSerializer(serializers.Serializer):
    group_pk_list = serializers.CharField(
        help_text=_(
            'Comma separated list of group primary keys to assign this '
            'user to.'
        )
    )

    def create(self, validated_data):
        validated_data['user'].groups.clear()
        try:
            pk_list = validated_data['group_pk_list'].split(',')

            for group in Group.objects.filter(pk__in=pk_list):
                validated_data['user'].groups.add(group)
        except Exception as exception:
            raise ValidationError(exception)

        return {'group_pk_list': validated_data['group_pk_list']}


class UserSerializer(serializers.HyperlinkedModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    groups_pk_list = serializers.CharField(
        help_text=_(
            'List of group primary keys to which to add the user.'
        ), required=False
    )
    password = serializers.CharField(
        required=False, style={'input_type': 'password'}, write_only=True
    )

    class Meta:
        extra_kwargs = {
            'url': {'view_name': 'rest_api:user-detail'}
        }
        fields = (
            'first_name', 'date_joined', 'email', 'groups', 'groups_pk_list',
            'id', 'is_active', 'last_login', 'last_name', 'password', 'url',
            'username'
        )
        model = get_user_model()
        read_only_fields = ('groups', 'is_active', 'last_login', 'date_joined')
        write_only_fields = ('password', 'group_pk_list')

    def _add_groups(self, instance):
        instance.groups.add(
            *Group.objects.filter(pk__in=self.groups_pk_list.split(','))
        )

    def create(self, validated_data):
        self.groups_pk_list = validated_data.pop('groups_pk_list', '')
        password = validated_data.pop('password', None)
        instance = super(UserSerializer, self).create(validated_data)

        if password:
            instance.set_password(password)
            instance.save()

        if self.groups_pk_list:
            self._add_groups(instance=instance)

        return instance

    def update(self, instance, validated_data):
        self.groups_pk_list = validated_data.pop('groups_pk_list', '')

        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            validated_data.pop('password')

        instance = super(UserSerializer, self).update(instance, validated_data)

        if self.groups_pk_list:
            instance.groups.clear()
            self._add_groups(instance=instance)

        return instance

    def validate(self, data):
        if 'password' in data:
            validate_password(data['password'], self.instance)

        return data
