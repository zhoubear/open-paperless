from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse

from rest_framework.test import APITestCase

from documents.models import DocumentType
from documents.permissions import permission_document_view
from documents.tests.literals import (
    TEST_DOCUMENT_TYPE_LABEL, TEST_SMALL_DOCUMENT_PATH
)
from permissions.classes import Permission
from permissions.models import Role
from permissions.tests.literals import TEST_ROLE_LABEL
from user_management.tests.literals import (
    TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME
)

from ..models import AccessControlList
from ..permissions import permission_acl_view


@override_settings(OCR_AUTO_OCR=False)
class ACLAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username=TEST_ADMIN_USERNAME, email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )

        self.client.login(
            username=TEST_ADMIN_USERNAME, password=TEST_ADMIN_PASSWORD
        )

        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object
            )

        self.role = Role.objects.create(label=TEST_ROLE_LABEL)

        self.document_content_type = ContentType.objects.get_for_model(
            self.document
        )
        Permission.invalidate_cache()

    def tearDown(self):
        if hasattr(self, 'document_type'):
            self.document_type.delete()

    def _create_acl(self):
        self.acl = AccessControlList.objects.create(
            content_object=self.document,
            role=self.role
        )

        self.acl.permissions.add(permission_document_view.stored_permission)

    def test_object_acl_list_view(self):
        self._create_acl()

        response = self.client.get(
            reverse(
                'rest_api:accesscontrollist-list',
                args=(
                    self.document_content_type.app_label,
                    self.document_content_type.model,
                    self.document.pk
                )
            )
        )

        self.assertEqual(
            response.data['results'][0]['content_type']['app_label'],
            self.document_content_type.app_label
        )
        self.assertEqual(
            response.data['results'][0]['role']['label'], TEST_ROLE_LABEL
        )

    def test_object_acl_delete_view(self):
        self._create_acl()

        response = self.client.delete(
            reverse(
                'rest_api:accesscontrollist-detail',
                args=(
                    self.document_content_type.app_label,
                    self.document_content_type.model,
                    self.document.pk, self.acl.pk
                )
            )
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(AccessControlList.objects.count(), 0)

    def test_object_acl_detail_view(self):
        self._create_acl()

        response = self.client.get(
            reverse(
                'rest_api:accesscontrollist-detail',
                args=(
                    self.document_content_type.app_label,
                    self.document_content_type.model,
                    self.document.pk, self.acl.pk
                )
            )
        )
        self.assertEqual(
            response.data['content_type']['app_label'],
            self.document_content_type.app_label
        )
        self.assertEqual(
            response.data['role']['label'], TEST_ROLE_LABEL
        )

    def test_object_acl_permission_delete_view(self):
        self._create_acl()
        permission = self.acl.permissions.first()

        response = self.client.delete(
            reverse(
                'rest_api:accesscontrollist-permission-detail',
                args=(
                    self.document_content_type.app_label,
                    self.document_content_type.model,
                    self.document.pk, self.acl.pk,
                    permission.pk
                )
            )
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.acl.permissions.count(), 0)

    def test_object_acl_permission_detail_view(self):
        self._create_acl()
        permission = self.acl.permissions.first()

        response = self.client.get(
            reverse(
                'rest_api:accesscontrollist-permission-detail',
                args=(
                    self.document_content_type.app_label,
                    self.document_content_type.model,
                    self.document.pk, self.acl.pk,
                    permission.pk
                )
            )
        )

        self.assertEqual(
            response.data['pk'], permission_document_view.pk
        )

    def test_object_acl_permission_list_view(self):
        self._create_acl()

        response = self.client.get(
            reverse(
                'rest_api:accesscontrollist-permission-list',
                args=(
                    self.document_content_type.app_label,
                    self.document_content_type.model,
                    self.document.pk, self.acl.pk
                )
            )
        )

        self.assertEqual(
            response.data['results'][0]['pk'],
            permission_document_view.pk
        )

    def test_object_acl_permission_list_post_view(self):
        self._create_acl()

        response = self.client.post(
            reverse(
                'rest_api:accesscontrollist-permission-list',
                args=(
                    self.document_content_type.app_label,
                    self.document_content_type.model,
                    self.document.pk, self.acl.pk
                )
            ), data={'permission_pk': permission_acl_view.pk}
        )

        self.assertEqual(response.status_code, 201)
        self.assertQuerysetEqual(
            ordered=False, qs=self.acl.permissions.all(), values=(
                repr(permission_document_view.stored_permission),
                repr(permission_acl_view.stored_permission)
            )
        )

    def test_object_acl_post_no_permissions_added_view(self):
        response = self.client.post(
            reverse(
                'rest_api:accesscontrollist-list',
                args=(
                    self.document_content_type.app_label,
                    self.document_content_type.model,
                    self.document.pk
                )
            ), data={'role_pk': self.role.pk}
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            self.document.acls.first().role, self.role
        )
        self.assertEqual(
            self.document.acls.first().content_object, self.document
        )
        self.assertEqual(
            self.document.acls.first().permissions.count(), 0
        )

    def test_object_acl_post_with_permissions_added_view(self):
        response = self.client.post(
            reverse(
                'rest_api:accesscontrollist-list',
                args=(
                    self.document_content_type.app_label,
                    self.document_content_type.model,
                    self.document.pk
                )
            ), data={
                'role_pk': self.role.pk,
                'permissions_pk_list': permission_acl_view.pk

            }
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            self.document.acls.first().content_object, self.document
        )
        self.assertEqual(
            self.document.acls.first().role, self.role
        )
        self.assertEqual(
            self.document.acls.first().permissions.first(),
            permission_acl_view.stored_permission
        )
