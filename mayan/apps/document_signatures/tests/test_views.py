from __future__ import absolute_import, unicode_literals

import logging

from django.core.files import File

from django_downloadview.test import assert_download_response

from django_gpg.models import Key
from documents.models import DocumentVersion
from documents.tests.literals import TEST_DOCUMENT_PATH
from documents.tests.test_views import GenericDocumentViewTestCase

from ..models import DetachedSignature, EmbeddedSignature
from ..permissions import (
    permission_document_version_signature_delete,
    permission_document_version_signature_download,
    permission_document_version_signature_upload,
    permission_document_version_signature_verify,
    permission_document_version_signature_view
)

from .literals import (
    TEST_SIGNATURE_FILE_PATH, TEST_SIGNED_DOCUMENT_PATH, TEST_KEY_FILE
)

TEST_UNSIGNED_DOCUMENT_COUNT = 4
TEST_SIGNED_DOCUMENT_COUNT = 2


class SignaturesViewTestCase(GenericDocumentViewTestCase):
    def test_signature_list_view_no_permission(self):
        with open(TEST_KEY_FILE) as file_object:
            Key.objects.create(key_data=file_object.read())

        with open(TEST_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object
            )

        with open(TEST_SIGNATURE_FILE_PATH) as file_object:
            DetachedSignature.objects.create(
                document_version=document.latest_version,
                signature_file=File(file_object)
            )

        self.login_user()

        response = self.get(
            'signatures:document_version_signature_list',
            args=(document.latest_version.pk,)
        )

        self.assertEqual(response.status_code, 403)

    def test_signature_list_view_with_access(self):
        with open(TEST_KEY_FILE) as file_object:
            Key.objects.create(key_data=file_object.read())

        with open(TEST_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object
            )

        with open(TEST_SIGNATURE_FILE_PATH) as file_object:
            DetachedSignature.objects.create(
                document_version=document.latest_version,
                signature_file=File(file_object)
            )

        self.login_user()

        self.grant_access(
            obj=document,
            permission=permission_document_version_signature_view
        )

        response = self.get(
            'signatures:document_version_signature_list',
            args=(document.latest_version.pk,)
        )

        self.assertContains(response, 'Total: 1', status_code=200)

    def test_signature_detail_view_no_permission(self):
        with open(TEST_KEY_FILE) as file_object:
            Key.objects.create(key_data=file_object.read())

        with open(TEST_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object
            )

        with open(TEST_SIGNATURE_FILE_PATH) as file_object:
            signature = DetachedSignature.objects.create(
                document_version=document.latest_version,
                signature_file=File(file_object)
            )

        self.login_user()

        response = self.get(
            'signatures:document_version_signature_details',
            args=(signature.pk,)
        )

        self.assertEqual(response.status_code, 403)

    def test_signature_detail_view_with_access(self):
        with open(TEST_KEY_FILE) as file_object:
            Key.objects.create(key_data=file_object.read())

        with open(TEST_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object
            )

        with open(TEST_SIGNATURE_FILE_PATH) as file_object:
            signature = DetachedSignature.objects.create(
                document_version=document.latest_version,
                signature_file=File(file_object)
            )

        self.login_user()

        self.grant_access(
            obj=document,
            permission=permission_document_version_signature_view
        )

        response = self.get(
            'signatures:document_version_signature_details',
            args=(signature.pk,)
        )

        self.assertContains(response, signature.signature_id, status_code=200)

    def test_signature_upload_view_no_permission(self):
        with open(TEST_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object
            )

        self.login_user()

        with open(TEST_SIGNATURE_FILE_PATH) as file_object:
            response = self.post(
                'signatures:document_version_signature_upload',
                args=(document.latest_version.pk,),
                data={'signature_file': file_object}
            )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(DetachedSignature.objects.count(), 0)

    def test_signature_upload_view_with_access(self):
        with open(TEST_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object
            )

        self.login_user()

        self.grant_access(
            obj=document,
            permission=permission_document_version_signature_upload
        )

        with open(TEST_SIGNATURE_FILE_PATH) as file_object:
            response = self.post(
                'signatures:document_version_signature_upload',
                args=(document.latest_version.pk,),
                data={'signature_file': file_object}
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(DetachedSignature.objects.count(), 1)

    def test_signature_download_view_no_permission(self):
        with open(TEST_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object
            )

        with open(TEST_SIGNATURE_FILE_PATH) as file_object:
            signature = DetachedSignature.objects.create(
                document_version=document.latest_version,
                signature_file=File(file_object)
            )

        self.login_user()

        response = self.get(
            'signatures:document_version_signature_download',
            args=(signature.pk,),
        )

        self.assertEqual(response.status_code, 403)

    def test_signature_download_view_with_access(self):
        with open(TEST_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object
            )

        with open(TEST_SIGNATURE_FILE_PATH) as file_object:
            signature = DetachedSignature.objects.create(
                document_version=document.latest_version,
                signature_file=File(file_object)
            )

        self.login_user()

        self.grant_access(
            obj=document,
            permission=permission_document_version_signature_download
        )

        self.expected_content_type = 'application/octet-stream; charset=utf-8'

        response = self.get(
            'signatures:document_version_signature_download',
            args=(signature.pk,),
        )

        with signature.signature_file as file_object:
            assert_download_response(
                self, response=response, content=file_object.read(),
            )

    def test_signature_delete_view_no_permission(self):
        with open(TEST_KEY_FILE) as file_object:
            Key.objects.create(key_data=file_object.read())

        with open(TEST_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object
            )

        with open(TEST_SIGNATURE_FILE_PATH) as file_object:
            signature = DetachedSignature.objects.create(
                document_version=document.latest_version,
                signature_file=File(file_object)
            )

        self.login_user()

        self.grant_access(
            obj=document,
            permission=permission_document_version_signature_view
        )

        response = self.post(
            'signatures:document_version_signature_delete',
            args=(signature.pk,)
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(DetachedSignature.objects.count(), 1)

    def test_signature_delete_view_with_access(self):
        with open(TEST_KEY_FILE) as file_object:
            Key.objects.create(key_data=file_object.read())

        with open(TEST_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object
            )

        with open(TEST_SIGNATURE_FILE_PATH) as file_object:
            signature = DetachedSignature.objects.create(
                document_version=document.latest_version,
                signature_file=File(file_object)
            )

        self.login_user()

        self.grant_access(
            obj=document,
            permission=permission_document_version_signature_delete
        )
        self.grant_access(
            obj=document,
            permission=permission_document_version_signature_view
        )

        response = self.post(
            'signatures:document_version_signature_delete',
            args=(signature.pk,), follow=True
        )

        self.assertContains(response, 'deleted', status_code=200)
        self.assertEqual(DetachedSignature.objects.count(), 0)

    def test_missing_signature_verify_view_no_permission(self):
        # Silence converter logging
        logging.getLogger('converter.backends').setLevel(logging.CRITICAL)

        for document in self.document_type.documents.all():
            document.delete(to_trash=False)

        old_hooks = DocumentVersion._post_save_hooks
        DocumentVersion._post_save_hooks = {}
        for count in range(TEST_UNSIGNED_DOCUMENT_COUNT):
            with open(TEST_DOCUMENT_PATH) as file_object:
                self.document_type.new_document(
                    file_object=file_object
                )

        for count in range(TEST_SIGNED_DOCUMENT_COUNT):
            with open(TEST_SIGNED_DOCUMENT_PATH) as file_object:
                self.document_type.new_document(
                    file_object=file_object
                )

        self.assertEqual(
            EmbeddedSignature.objects.unsigned_document_versions().count(),
            TEST_UNSIGNED_DOCUMENT_COUNT + TEST_SIGNED_DOCUMENT_COUNT
        )

        DocumentVersion._post_save_hooks = old_hooks

        self.login_user()

        response = self.post(
            'signatures:all_document_version_signature_verify', follow=True
        )

        self.assertEqual(response.status_code, 403)

        self.assertEqual(
            EmbeddedSignature.objects.unsigned_document_versions().count(),
            TEST_UNSIGNED_DOCUMENT_COUNT + TEST_SIGNED_DOCUMENT_COUNT
        )

    def test_missing_signature_verify_view_with_permission(self):
        # Silence converter logging
        logging.getLogger('converter.backends').setLevel(logging.CRITICAL)

        for document in self.document_type.documents.all():
            document.delete(to_trash=False)

        old_hooks = DocumentVersion._post_save_hooks
        DocumentVersion._post_save_hooks = {}
        for count in range(TEST_UNSIGNED_DOCUMENT_COUNT):
            with open(TEST_DOCUMENT_PATH) as file_object:
                self.document_type.new_document(
                    file_object=file_object
                )

        for count in range(TEST_SIGNED_DOCUMENT_COUNT):
            with open(TEST_SIGNED_DOCUMENT_PATH) as file_object:
                self.document_type.new_document(
                    file_object=file_object
                )

        self.assertEqual(
            EmbeddedSignature.objects.unsigned_document_versions().count(),
            TEST_UNSIGNED_DOCUMENT_COUNT + TEST_SIGNED_DOCUMENT_COUNT
        )

        DocumentVersion._post_save_hooks = old_hooks

        self.login_user()

        self.grant_permission(
            permission=permission_document_version_signature_verify
        )

        response = self.post(
            'signatures:all_document_version_signature_verify', follow=True
        )

        self.assertContains(response, 'queued', status_code=200)

        self.assertEqual(
            EmbeddedSignature.objects.unsigned_document_versions().count(),
            TEST_UNSIGNED_DOCUMENT_COUNT
        )
