from __future__ import unicode_literals

import logging

from django.core.files.base import File
from documents.models import DocumentType
from documents.permissions import (
    permission_document_properties_edit, permission_document_view
)
from documents.tests.literals import (
    TEST_DOCUMENT_TYPE_2_LABEL, TEST_SMALL_DOCUMENT_PATH
)
from documents.tests.test_views import GenericDocumentViewTestCase

from ..models import MetadataType
from ..permissions import (
    permission_metadata_document_add, permission_metadata_document_remove,
    permission_metadata_document_edit
)

from .literals import (
    TEST_DOCUMENT_METADATA_VALUE_2, TEST_METADATA_TYPE_LABEL,
    TEST_METADATA_TYPE_LABEL_2, TEST_METADATA_TYPE_NAME,
    TEST_METADATA_TYPE_NAME_2, TEST_METADATA_VALUE_EDITED
)


class DocumentMetadataTestCase(GenericDocumentViewTestCase):
    def setUp(self):
        super(DocumentMetadataTestCase, self).setUp()

        self.metadata_type = MetadataType.objects.create(
            name=TEST_METADATA_TYPE_NAME, label=TEST_METADATA_TYPE_LABEL
        )

        self.document_type.metadata.create(metadata_type=self.metadata_type)

    def test_metadata_add_view_no_permission(self):
        self.login_user()

        self.grant_permission(permission=permission_document_view)

        response = self.post(
            'metadata:metadata_add', args=(self.document.pk,),
            data={'metadata_type': self.metadata_type.pk}
        )
        self.assertNotContains(
            response, text=self.metadata_type.label, status_code=200
        )

        self.assertEqual(len(self.document.metadata.all()), 0)

    def test_metadata_add_view_with_permission(self):
        self.login_user()

        self.grant_permission(permission=permission_document_view)
        self.grant_permission(permission=permission_metadata_document_add)
        self.grant_permission(permission=permission_metadata_document_edit)

        response = self.post(
            'metadata:metadata_add', args=(self.document.pk,),
            data={'metadata_type': self.metadata_type.pk}, follow=True
        )
        self.assertContains(response, 'successfully', status_code=200)

        self.assertEqual(len(self.document.metadata.all()), 1)

    def test_metadata_edit_after_document_type_change(self):
        # Gitlab issue #204
        # Problems to add required metadata after changing the document type

        self.login_user()

        self.grant_permission(permission=permission_document_properties_edit)
        self.grant_permission(permission=permission_metadata_document_edit)

        document_type_2 = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_2_LABEL
        )

        metadata_type_2 = MetadataType.objects.create(
            name=TEST_METADATA_TYPE_NAME_2, label=TEST_METADATA_TYPE_LABEL_2
        )

        document_metadata_2 = document_type_2.metadata.create(
            metadata_type=metadata_type_2, required=True
        )

        self.document.set_document_type(document_type=document_type_2)

        response = self.get(
            'metadata:metadata_edit', args=(self.document.pk,), follow=True
        )

        self.assertContains(response, 'Edit', status_code=200)

        response = self.post(
            'metadata:metadata_edit', args=(self.document.pk,), data={
                'form-0-id': document_metadata_2.metadata_type.pk,
                'form-0-update': True,
                'form-0-value': TEST_DOCUMENT_METADATA_VALUE_2,
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MAX_NUM_FORMS': '',
            }, follow=True
        )

        self.assertContains(response, 'Metadata for document', status_code=200)

        self.assertEqual(
            self.document.metadata.get(metadata_type=metadata_type_2).value,
            TEST_DOCUMENT_METADATA_VALUE_2
        )

    def test_metadata_remove_view_no_permission(self):
        self.login_user()

        document_metadata = self.document.metadata.create(
            metadata_type=self.metadata_type, value=''
        )

        self.assertEqual(len(self.document.metadata.all()), 1)

        self.grant_permission(permission=permission_document_view)

        # Test display of metadata removal form
        response = self.get(
            'metadata:metadata_remove', args=(self.document.pk,),
        )

        self.assertNotContains(
            response, text=self.metadata_type.label, status_code=200
        )

        # Test post to metadata removal view
        response = self.post(
            'metadata:metadata_remove', args=(self.document.pk,), data={
                'form-0-id': document_metadata.metadata_type.pk,
                'form-0-update': True,
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MAX_NUM_FORMS': '',
            }, follow=True
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(self.document.metadata.all()), 1)

    def test_metadata_remove_view_with_permission(self):
        # Silence unrelated logging
        logging.getLogger('navigation.classes').setLevel(logging.CRITICAL)

        self.login_user()

        document_metadata = self.document.metadata.create(
            metadata_type=self.metadata_type, value=''
        )

        self.assertEqual(len(self.document.metadata.all()), 1)

        self.grant_permission(permission=permission_document_view)
        self.grant_permission(permission=permission_metadata_document_remove)

        # Test display of metadata removal form
        response = self.get(
            'metadata:metadata_remove', args=(self.document.pk,),
        )

        self.assertContains(
            response, text=self.metadata_type.label, status_code=200
        )

        self.assertContains(response, 'emove', status_code=200)

        # Test post to metadata removal view
        response = self.post(
            'metadata:metadata_remove', args=(self.document.pk,), data={
                'form-0-id': document_metadata.metadata_type.pk,
                'form-0-update': True,
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MAX_NUM_FORMS': '',
            }, follow=True
        )

        self.assertContains(response, 'Success', status_code=200)

        self.assertEqual(len(self.document.metadata.all()), 0)

    def test_multiple_document_metadata_edit(self):
        self.login_user()

        self.grant_permission(permission=permission_document_view)
        self.grant_permission(permission=permission_metadata_document_add)
        self.grant_permission(permission=permission_metadata_document_edit)

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            document_2 = self.document_type.new_document(
                file_object=File(file_object)
            )

        document_metadata = self.document.metadata.create(
            metadata_type=self.metadata_type
        )
        document_2.metadata.create(metadata_type=self.metadata_type)

        response = self.get(
            'metadata:metadata_multiple_edit', data={
                'id_list': '{},{}'.format(self.document.pk, document_2.pk)
            }
        )

        self.assertContains(response, 'Edit', status_code=200)

        # Test post to metadata removal view
        response = self.post(
            'metadata:metadata_multiple_edit', data={
                'id_list': '{},{}'.format(self.document.pk, document_2.pk),
                'form-0-id': document_metadata.metadata_type.pk,
                'form-0-value': TEST_METADATA_VALUE_EDITED,
                'form-0-update': True,
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MAX_NUM_FORMS': '',
            }, follow=True
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            self.document.metadata.first().value, TEST_METADATA_VALUE_EDITED
        )
        self.assertEqual(
            document_2.metadata.first().value, TEST_METADATA_VALUE_EDITED
        )

    def test_multiple_document_metadata_remove(self):
        self.login_user()

        self.grant_permission(permission=permission_document_view)
        self.grant_permission(permission=permission_metadata_document_remove)

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            document_2 = self.document_type.new_document(
                file_object=File(file_object)
            )

        document_metadata = self.document.metadata.create(
            metadata_type=self.metadata_type
        )
        document_2.metadata.create(metadata_type=self.metadata_type)

        response = self.get(
            'metadata:metadata_multiple_remove', data={
                'id_list': '{},{}'.format(self.document.pk, document_2.pk)
            }
        )

        self.assertEquals(response.status_code, 200)

        # Test post to metadata removal view
        response = self.post(
            'metadata:metadata_multiple_remove', data={
                'id_list': '{},{}'.format(self.document.pk, document_2.pk),
                'form-0-id': document_metadata.metadata_type.pk,
                'form-0-update': True,
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MAX_NUM_FORMS': '',
            }, follow=True
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.document.metadata.count(), 0)
        self.assertEqual(document_2.metadata.count(), 0)

    def test_multiple_document_metadata_add(self):
        self.login_user()

        self.grant_permission(permission=permission_document_view)
        self.grant_permission(permission=permission_metadata_document_add)
        self.grant_permission(permission=permission_metadata_document_edit)

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            document_2 = self.document_type.new_document(
                file_object=File(file_object)
            )

        response = self.post(
            'metadata:metadata_multiple_add', data={
                'id_list': '{},{}'.format(self.document.pk, document_2.pk),
                'metadata_type': self.metadata_type.pk
            }, follow=True
        )

        self.assertContains(response, 'Edit', status_code=200)
