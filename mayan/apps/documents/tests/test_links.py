# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import time

from django.urls import reverse

from acls.models import AccessControlList

from ..links import (
    link_document_restore, link_document_version_download,
    link_document_version_revert
)
from ..permissions import (
    permission_document_download, permission_document_restore,
    permission_document_version_revert
)

from .literals import TEST_SMALL_DOCUMENT_PATH
from .test_views import GenericDocumentViewTestCase


class DocumentsLinksTestCase(GenericDocumentViewTestCase):
    def test_document_version_revert_link_no_permission(self):
        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document.new_version(file_object=file_object)

        self.assertTrue(self.document.versions.count(), 2)

        self.login_user()

        self.add_test_view(test_object=self.document.versions.first())
        context = self.get_test_view()
        resolved_link = link_document_version_revert.resolve(context=context)

        self.assertEqual(resolved_link, None)

    def test_document_version_revert_link_with_permission(self):
        # Needed by MySQL as milliseconds value is not store in timestamp
        # field
        time.sleep(2)

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document.new_version(file_object=file_object)

        self.assertTrue(self.document.versions.count(), 2)

        self.login_user()

        acl = AccessControlList.objects.create(
            content_object=self.document, role=self.role
        )
        acl.permissions.add(
            permission_document_version_revert.stored_permission
        )

        self.add_test_view(test_object=self.document.versions.first())
        context = self.get_test_view()
        resolved_link = link_document_version_revert.resolve(context=context)

        self.assertNotEqual(resolved_link, None)
        self.assertEqual(
            resolved_link.url,
            reverse(
                'documents:document_version_revert',
                args=(self.document.versions.first().pk,)
            )
        )

    def test_document_version_download_link_no_permission(self):
        self.login_user()

        self.add_test_view(test_object=self.document.latest_version)
        context = self.get_test_view()
        resolved_link = link_document_version_download.resolve(context=context)

        self.assertEqual(resolved_link, None)

    def test_document_version_download_link_with_permission(self):
        self.login_user()

        acl = AccessControlList.objects.create(
            content_object=self.document, role=self.role
        )
        acl.permissions.add(permission_document_download.stored_permission)

        self.add_test_view(test_object=self.document.latest_version)
        context = self.get_test_view()
        resolved_link = link_document_version_download.resolve(context=context)

        self.assertNotEqual(resolved_link, None)
        self.assertEqual(
            resolved_link.url,
            reverse(
                'documents:document_version_download_form',
                args=(self.document.latest_version.pk,)
            )
        )


class DeletedDocumentsLinksTestCase(GenericDocumentViewTestCase):
    def test_deleted_document_restore_link_no_permission(self):
        self.document.delete()

        self.login_user()

        self.add_test_view(test_object=self.document)
        context = self.get_test_view()
        resolved_link = link_document_restore.resolve(context=context)

        self.assertEqual(resolved_link, None)

    def test_deleted_document_restore_link_with_permission(self):
        self.document.delete()

        self.login_user()

        acl = AccessControlList.objects.create(
            content_object=self.document, role=self.role
        )
        acl.permissions.add(
            permission_document_restore.stored_permission
        )

        self.add_test_view(test_object=self.document)
        context = self.get_test_view()
        resolved_link = link_document_restore.resolve(context=context)

        self.assertNotEqual(resolved_link, None)
        self.assertEqual(
            resolved_link.url,
            reverse(
                'documents:document_restore',
                args=(self.document.pk,)
            )
        )
