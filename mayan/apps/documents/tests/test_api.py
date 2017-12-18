# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import time

from json import loads

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django.utils.encoding import force_text

from django_downloadview import assert_download_response
from rest_framework import status

from rest_api.tests import BaseAPITestCase
from user_management.tests.literals import (
    TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME
)

from .literals import (
    TEST_DOCUMENT_DESCRIPTION_EDITED, TEST_DOCUMENT_FILENAME,
    TEST_DOCUMENT_PATH, TEST_DOCUMENT_TYPE_LABEL,
    TEST_DOCUMENT_TYPE_LABEL_EDITED, TEST_DOCUMENT_VERSION_COMMENT_EDITED,
    TEST_SMALL_DOCUMENT_FILENAME, TEST_SMALL_DOCUMENT_PATH
)
from ..models import Document, DocumentType


class DocumentTypeAPITestCase(BaseAPITestCase):
    def setUp(self):
        super(DocumentTypeAPITestCase, self).setUp()
        self.admin_user = get_user_model().objects.create_superuser(
            username=TEST_ADMIN_USERNAME, email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )

        self.client.login(
            username=TEST_ADMIN_USERNAME, password=TEST_ADMIN_PASSWORD
        )

    def tearDown(self):
        self.admin_user.delete()
        super(DocumentTypeAPITestCase, self).tearDown()

    def test_document_type_create(self):
        self.assertEqual(DocumentType.objects.all().count(), 0)

        response = self.client.post(
            reverse('rest_api:documenttype-list'), data={
                'label': TEST_DOCUMENT_TYPE_LABEL
            }
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(DocumentType.objects.all().count(), 1)
        self.assertEqual(
            DocumentType.objects.all().first().label, TEST_DOCUMENT_TYPE_LABEL
        )

    def test_document_type_edit_via_put(self):
        document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        self.client.put(
            reverse('rest_api:documenttype-detail', args=(document_type.pk,)),
            {'label': TEST_DOCUMENT_TYPE_LABEL_EDITED}
        )

        document_type = DocumentType.objects.get(pk=document_type.pk)
        self.assertEqual(document_type.label, TEST_DOCUMENT_TYPE_LABEL_EDITED)

    def test_document_type_edit_via_patch(self):
        document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        self.client.patch(
            reverse('rest_api:documenttype-detail', args=(document_type.pk,)),
            {'label': TEST_DOCUMENT_TYPE_LABEL_EDITED}
        )

        document_type = DocumentType.objects.get(pk=document_type.pk)
        self.assertEqual(document_type.label, TEST_DOCUMENT_TYPE_LABEL_EDITED)

    def test_document_type_delete(self):
        document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        self.client.delete(
            reverse('rest_api:documenttype-detail', args=(document_type.pk,))
        )

        self.assertEqual(DocumentType.objects.all().count(), 0)


@override_settings(OCR_AUTO_OCR=False)
class DocumentAPITestCase(BaseAPITestCase):
    def setUp(self):
        super(DocumentAPITestCase, self).setUp()
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

    def tearDown(self):
        self.admin_user.delete()
        self.document_type.delete()
        super(DocumentAPITestCase, self).tearDown()

    def _create_document(self):
        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object,
                label=TEST_SMALL_DOCUMENT_FILENAME
            )

        # For compatibility
        return self.document

    def test_document_upload(self):
        with open(TEST_DOCUMENT_PATH) as file_descriptor:
            response = self.client.post(
                reverse('rest_api:document-list'), {
                    'document_type': self.document_type.pk,
                    'file': file_descriptor
                }
            )

        document_data = loads(response.content)

        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )
        self.assertEqual(Document.objects.count(), 1)

        document = Document.objects.first()

        self.assertEqual(document.pk, document_data['id'])

        self.assertEqual(document.versions.count(), 1)

        self.assertEqual(document.exists(), True)
        self.assertEqual(document.size, 272213)

        self.assertEqual(document.file_mimetype, 'application/pdf')
        self.assertEqual(document.file_mime_encoding, 'binary')
        self.assertEqual(document.label, TEST_DOCUMENT_FILENAME)
        self.assertEqual(
            document.checksum,
            'c637ffab6b8bb026ed3784afdb07663fddc60099853fae2be93890852a69ecf3'
        )
        self.assertEqual(document.page_count, 47)

    def test_document_new_version_upload(self):
        document = self._create_document()

        # Artifical delay since MySQL doesn't store microsecond data in
        # timestamps. Version timestamp is used to determine which version
        # is the latest.
        time.sleep(1)
        with open(TEST_DOCUMENT_PATH) as file_descriptor:
            response = self.client.post(
                reverse(
                    'rest_api:document-version-list', args=(document.pk,)
                ), {
                    'comment': '',
                    'file': file_descriptor,
                }
            )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        self.assertEqual(document.versions.count(), 2)
        self.assertEqual(document.exists(), True)
        self.assertEqual(document.size, 272213)
        self.assertEqual(document.file_mimetype, 'application/pdf')
        self.assertEqual(document.file_mime_encoding, 'binary')
        self.assertEqual(
            document.checksum,
            'c637ffab6b8bb026ed3784afdb07663fddc60099853fae2be93890852a69ecf3'
        )
        self.assertEqual(document.page_count, 47)

    def test_document_version_revert(self):
        document = self._create_document()

        # Needed by MySQL as milliseconds value is not store in timestamp field
        time.sleep(1)

        with open(TEST_DOCUMENT_PATH) as file_object:
            document.new_version(file_object=file_object)

        self.assertEqual(document.versions.count(), 2)

        last_version = document.versions.last()

        self.client.delete(
            reverse(
                'rest_api:documentversion-detail',
                args=(document.pk, last_version.pk,)
            )
        )

        self.assertEqual(document.versions.count(), 1)

        self.assertEqual(document.versions.first(), document.latest_version)

    def test_document_version_list(self):
        document = self._create_document()

        # Needed by MySQL as milliseconds value is not store in timestamp field
        time.sleep(1)

        with open(TEST_DOCUMENT_PATH) as file_object:
            document.new_version(file_object=file_object)

        document.refresh_from_db()

        self.assertEqual(document.versions.count(), 2)

        response = self.client.get(
            reverse(
                'rest_api:document-version-list',
                args=(document.pk,)
            )
        )

        self.assertEqual(
            response.data['results'][1]['checksum'],
            document.latest_version.checksum
        )

    def test_document_download(self):
        document = self._create_document()

        response = self.client.get(
            reverse(
                'rest_api:document-download', args=(document.pk,)
            )
        )

        with document.open() as file_object:
            assert_download_response(
                self, response, content=file_object.read(),
                basename=TEST_SMALL_DOCUMENT_FILENAME,
                mime_type='{}; charset=utf-8'.format(document.file_mimetype)
            )

    def test_document_version_download(self):
        document = self._create_document()

        latest_version = document.latest_version
        response = self.client.get(
            reverse(
                'rest_api:documentversion-download',
                args=(document.pk, latest_version.pk,)
            )
        )

        with latest_version.open() as file_object:
            assert_download_response(
                self, response, content=file_object.read(),
                basename=force_text(latest_version),
                mime_type='{}; charset=utf-8'.format(document.file_mimetype)
            )

    def test_document_version_download_preserve_extension(self):
        document = self._create_document()

        latest_version = document.latest_version
        response = self.client.get(
            reverse(
                'rest_api:documentversion-download',
                args=(document.pk, latest_version.pk,)
            ), data={'preserve_extension': True}
        )

        with latest_version.open() as file_object:
            assert_download_response(
                self, response, content=file_object.read(),
                basename=latest_version.get_rendered_string(
                    preserve_extension=True
                ), mime_type='{}; charset=utf-8'.format(
                    document.file_mimetype
                )
            )

    def test_document_version_edit_via_patch(self):
        self._create_document()
        response = self.client.patch(
            reverse(
                'rest_api:documentversion-detail',
                args=(self.document.pk, self.document.latest_version.pk,)
            ), data={'comment': TEST_DOCUMENT_VERSION_COMMENT_EDITED}
        )

        self.assertEqual(response.status_code, 200)
        self.document.latest_version.refresh_from_db()
        self.assertEqual(self.document.versions.count(), 1)
        self.assertEqual(
            self.document.latest_version.comment,
            TEST_DOCUMENT_VERSION_COMMENT_EDITED
        )

    def test_document_version_edit_via_put(self):
        self._create_document()
        response = self.client.put(
            reverse(
                'rest_api:documentversion-detail',
                args=(self.document.pk, self.document.latest_version.pk,)
            ), data={'comment': TEST_DOCUMENT_VERSION_COMMENT_EDITED}
        )

        self.assertEqual(response.status_code, 200)
        self.document.latest_version.refresh_from_db()
        self.assertEqual(self.document.versions.count(), 1)
        self.assertEqual(
            self.document.latest_version.comment,
            TEST_DOCUMENT_VERSION_COMMENT_EDITED
        )

    def test_document_comment_edit_via_patch(self):
        self._create_document()
        response = self.client.patch(
            reverse(
                'rest_api:document-detail',
                args=(self.document.pk,)
            ), data={'description': TEST_DOCUMENT_DESCRIPTION_EDITED}
        )

        self.assertEqual(response.status_code, 200)
        self.document.refresh_from_db()
        self.assertEqual(
            self.document.description,
            TEST_DOCUMENT_DESCRIPTION_EDITED
        )

    def test_document_comment_edit_via_put(self):
        self._create_document()
        response = self.client.put(
            reverse(
                'rest_api:document-detail',
                args=(self.document.pk,)
            ), data={'description': TEST_DOCUMENT_DESCRIPTION_EDITED}
        )
        self.assertEqual(response.status_code, 200)
        self.document.refresh_from_db()
        self.assertEqual(
            self.document.description,
            TEST_DOCUMENT_DESCRIPTION_EDITED
        )


@override_settings(OCR_AUTO_OCR=False)
class TrashedDocumentAPITestCase(BaseAPITestCase):
    def setUp(self):
        super(TrashedDocumentAPITestCase, self).setUp()
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

    def tearDown(self):
        self.admin_user.delete()
        self.document_type.delete()
        super(TrashedDocumentAPITestCase, self).tearDown()

    def _create_document(self):
        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object,
            )

        return document

    def test_document_move_to_trash(self):
        document = self._create_document()

        self.client.delete(
            reverse('rest_api:document-detail', args=(document.pk,))
        )

        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(Document.trash.count(), 1)

    def test_trashed_document_delete_from_trash(self):
        document = self._create_document()
        document.delete()

        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(Document.trash.count(), 1)

        self.client.delete(
            reverse('rest_api:trasheddocument-detail', args=(document.pk,))
        )

        self.assertEqual(Document.trash.count(), 0)

    def test_trashed_document_detail_view(self):
        document = self._create_document()
        document.delete()

        response = self.client.get(
            reverse('rest_api:trasheddocument-detail', args=(document.pk,))
        )

        self.assertEqual(response.data['uuid'], force_text(document.uuid))

    def test_trashed_document_list_view(self):
        document = self._create_document()
        document.delete()

        response = self.client.get(
            reverse('rest_api:trasheddocument-list')
        )

        self.assertEqual(response.data['results'][0]['uuid'], force_text(document.uuid))

    def test_trashed_document_restore(self):
        document = self._create_document()
        document.delete()

        self.client.post(
            reverse('rest_api:trasheddocument-restore', args=(document.pk,))
        )

        self.assertEqual(Document.trash.count(), 0)
        self.assertEqual(Document.objects.count(), 1)
