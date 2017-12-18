from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

from rest_api.tests import BaseAPITestCase
from user_management.tests.literals import (
    TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME,
    TEST_GROUP_NAME
)

from ..classes import Permission
from ..models import Role
from ..permissions import permission_role_view

from .literals import TEST_ROLE_LABEL, TEST_ROLE_LABEL_EDITED


class PermissionAPITestCase(BaseAPITestCase):
    def setUp(self):
        super(PermissionAPITestCase, self).setUp()
        self.admin_user = get_user_model().objects.create_superuser(
            username=TEST_ADMIN_USERNAME, email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )

        self.client.login(
            username=TEST_ADMIN_USERNAME, password=TEST_ADMIN_PASSWORD
        )

        Permission.invalidate_cache()

    def test_permissions_list_view(self):
        response = self.client.get(reverse('rest_api:permission-list'))
        self.assertEqual(response.status_code, 200)

    def _create_role(self):
        self.role = Role.objects.create(label=TEST_ROLE_LABEL)

    def test_roles_list_view(self):
        self._create_role()

        response = self.client.get(reverse('rest_api:role-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['label'], TEST_ROLE_LABEL)

    def _role_create_request(self, extra_data=None):
        data = {
            'label': TEST_ROLE_LABEL
        }

        if extra_data:
            data.update(extra_data)

        return self.client.post(
            reverse('rest_api:role-list'), data=data
        )

    def test_role_create_view(self):
        response = self._role_create_request()
        role = Role.objects.first()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'label': role.label, 'id': role.pk})
        self.assertEqual(Role.objects.count(), 1)
        self.assertEqual(role.label, TEST_ROLE_LABEL)

    def _create_group(self):
        self.group = Group.objects.create(name=TEST_GROUP_NAME)

    def test_role_create_complex_view(self):
        self._create_group()

        response = self._role_create_request(
            extra_data={
                'groups_pk_list': '{}'.format(self.group.pk),
                'permissions_pk_list': '{}'.format(permission_role_view.pk)
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Role.objects.count(), 1)
        self.assertEqual(Role.objects.first().label, TEST_ROLE_LABEL)
        self.assertQuerysetEqual(
            Role.objects.first().groups.all(), (repr(self.group),)
        )
        self.assertQuerysetEqual(
            Role.objects.first().permissions.all(),
            (repr(permission_role_view.stored_permission),)
        )

    def _role_edit_request(self, extra_data=None, request_type='patch'):
        data = {
            'label': TEST_ROLE_LABEL_EDITED
        }

        if extra_data:
            data.update(extra_data)

        return getattr(self.client, request_type)(
            reverse('rest_api:role-detail', args=(self.role.pk,)), data=data
        )

    def test_role_edit_via_patch(self):
        self._create_role()
        response = self._role_edit_request()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Role.objects.first().label, TEST_ROLE_LABEL_EDITED)

    def test_role_edit_complex_via_patch(self):
        Role.objects.all().delete()
        Group.objects.all().delete()

        self._create_role()
        self._create_group()

        response = self._role_edit_request(
            extra_data={
                'groups_pk_list': '{}'.format(self.group.pk),
                'permissions_pk_list': '{}'.format(permission_role_view.pk)
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Role.objects.first().label, TEST_ROLE_LABEL_EDITED)
        self.assertQuerysetEqual(
            Role.objects.first().groups.all(), (repr(self.group),)
        )
        self.assertQuerysetEqual(
            Role.objects.first().permissions.all(),
            (repr(permission_role_view.stored_permission),)
        )

    def test_role_edit_via_put(self):
        self._create_role()
        response = self._role_edit_request(request_type='put')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Role.objects.first().label, TEST_ROLE_LABEL_EDITED)

    def test_role_edit_complex_via_put(self):
        Role.objects.all().delete()
        Group.objects.all().delete()

        self._create_role()
        self._create_group()

        response = self._role_edit_request(
            extra_data={
                'groups_pk_list': '{}'.format(self.group.pk),
                'permissions_pk_list': '{}'.format(permission_role_view.pk)
            }, request_type='put'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Role.objects.first().label, TEST_ROLE_LABEL_EDITED)
        self.assertQuerysetEqual(
            Role.objects.first().groups.all(), (repr(self.group),)
        )
        self.assertQuerysetEqual(
            Role.objects.first().permissions.all(),
            (repr(permission_role_view.stored_permission),)
        )

    def test_role_delete_view(self):
        self._create_role()
        response = self.client.delete(
            reverse('rest_api:role-detail', args=(self.role.pk,))
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Role.objects.count(), 0)
