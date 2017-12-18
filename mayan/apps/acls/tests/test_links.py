from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from documents.tests.test_views import GenericDocumentViewTestCase

from ..links import (
    link_acl_delete, link_acl_list, link_acl_create, link_acl_permissions
)
from ..models import AccessControlList
from ..permissions import permission_acl_edit, permission_acl_view


class ACLsLinksTestCase(GenericDocumentViewTestCase):
    def test_document_acl_create_link(self):
        acl = AccessControlList.objects.create(
            content_object=self.document, role=self.role
        )

        acl.permissions.add(permission_acl_edit.stored_permission)
        self.login_user()

        self.add_test_view(test_object=self.document)
        context = self.get_test_view()
        resolved_link = link_acl_create.resolve(context=context)

        self.assertNotEqual(resolved_link, None)

        content_type = ContentType.objects.get_for_model(self.document)
        kwargs = {
            'app_label': content_type.app_label,
            'model': content_type.model,
            'object_id': self.document.pk
        }

        self.assertEqual(
            resolved_link.url, reverse('acls:acl_create', kwargs=kwargs)
        )

    def test_document_acl_delete_link(self):
        acl = AccessControlList.objects.create(
            content_object=self.document, role=self.role
        )

        acl.permissions.add(permission_acl_edit.stored_permission)
        self.login_user()

        self.add_test_view(test_object=acl)
        context = self.get_test_view()
        resolved_link = link_acl_delete.resolve(context=context)

        self.assertNotEqual(resolved_link, None)

        self.assertEqual(
            resolved_link.url, reverse('acls:acl_delete', args=(acl.pk,))
        )

    def test_document_acl_edit_link(self):
        acl = AccessControlList.objects.create(
            content_object=self.document, role=self.role
        )

        acl.permissions.add(permission_acl_edit.stored_permission)
        self.login_user()

        self.add_test_view(test_object=acl)
        context = self.get_test_view()
        resolved_link = link_acl_permissions.resolve(context=context)

        self.assertNotEqual(resolved_link, None)

        self.assertEqual(
            resolved_link.url, reverse('acls:acl_permissions', args=(acl.pk,))
        )

    def test_document_acl_list_link(self):
        acl = AccessControlList.objects.create(
            content_object=self.document, role=self.role
        )

        acl.permissions.add(permission_acl_view.stored_permission)
        self.login_user()

        self.add_test_view(test_object=self.document)
        context = self.get_test_view()
        resolved_link = link_acl_list.resolve(context=context)

        self.assertNotEqual(resolved_link, None)

        content_type = ContentType.objects.get_for_model(self.document)
        kwargs = {
            'app_label': content_type.app_label,
            'model': content_type.model,
            'object_id': self.document.pk
        }

        self.assertEqual(
            resolved_link.url, reverse('acls:acl_list', kwargs=kwargs)
        )
