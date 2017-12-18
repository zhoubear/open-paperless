from __future__ import unicode_literals

from django.test.client import Client
from django.urls import reverse

from common.tests import BaseTestCase
from user_management.tests import TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME

from ..models import Role

from .literals import TEST_ROLE_LABEL, TEST_ROLE_LABEL_EDITED


class PermissionsViewsTestCase(BaseTestCase):
    def setUp(self):
        super(PermissionsViewsTestCase, self).setUp()
        self.client = Client()
        # Login the admin user
        logged_in = self.client.login(
            username=TEST_ADMIN_USERNAME, password=TEST_ADMIN_PASSWORD
        )
        self.assertTrue(logged_in)
        self.assertTrue(self.admin_user.is_authenticated)

    def test_role_creation_view(self):
        self.role.delete()

        response = self.client.post(
            reverse(
                'permissions:role_create',
            ), data={
                'label': TEST_ROLE_LABEL,
            }, follow=True
        )

        self.assertContains(response, 'created', status_code=200)

        self.assertEqual(Role.objects.count(), 1)
        self.assertEqual(Role.objects.first().label, TEST_ROLE_LABEL)

    def test_role_delete_view(self):
        response = self.client.post(
            reverse(
                'permissions:role_delete', args=(self.role.pk,),
            ), follow=True
        )

        self.assertContains(response, 'deleted', status_code=200)

        self.assertEqual(Role.objects.count(), 0)

    def test_role_edit_view(self):
        response = self.client.post(
            reverse(
                'permissions:role_edit', args=(self.role.pk,),
            ), data={
                'label': TEST_ROLE_LABEL_EDITED,
            }, follow=True
        )

        self.assertContains(response, 'update', status_code=200)

        self.assertEqual(Role.objects.count(), 1)
        self.assertEqual(Role.objects.first().label, TEST_ROLE_LABEL_EDITED)
