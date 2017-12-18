from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

from documents.models import DocumentType
from documents.tests import TEST_DOCUMENT_TYPE_LABEL, TEST_SMALL_DOCUMENT_PATH
from rest_api.tests import BaseAPITestCase
from user_management.tests.literals import (
    TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME
)

from ..models import DocumentTypeMetadataType, MetadataType

from .literals import (
    TEST_METADATA_TYPE_LABEL, TEST_METADATA_TYPE_LABEL_2,
    TEST_METADATA_TYPE_NAME, TEST_METADATA_TYPE_NAME_2, TEST_METADATA_VALUE,
    TEST_METADATA_VALUE_EDITED
)


class MetadataTypeAPITestCase(BaseAPITestCase):
    def setUp(self):
        super(MetadataTypeAPITestCase, self).setUp()

        self.admin_user = get_user_model().objects.create_superuser(
            username=TEST_ADMIN_USERNAME, email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )

        self.client.login(
            username=TEST_ADMIN_USERNAME, password=TEST_ADMIN_PASSWORD
        )

    def _create_metadata_type(self):
        self.metadata_type = MetadataType.objects.create(
            label=TEST_METADATA_TYPE_LABEL, name=TEST_METADATA_TYPE_NAME
        )

    def test_metadata_type_create(self):
        response = self.client.post(
            reverse('rest_api:metadatatype-list'), data={
                'label': TEST_METADATA_TYPE_LABEL,
                'name': TEST_METADATA_TYPE_NAME
            }
        )

        metadata_type = MetadataType.objects.first()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['id'], metadata_type.pk)
        self.assertEqual(response.data['label'], TEST_METADATA_TYPE_LABEL)
        self.assertEqual(response.data['name'], TEST_METADATA_TYPE_NAME)

        self.assertEqual(metadata_type.label, TEST_METADATA_TYPE_LABEL)
        self.assertEqual(metadata_type.name, TEST_METADATA_TYPE_NAME)

    def test_metadata_type_delete(self):
        self._create_metadata_type()

        response = self.client.delete(
            reverse(
                'rest_api:metadatatype-detail',
                args=(self.metadata_type.pk,)
            )
        )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(MetadataType.objects.count(), 0)

    def test_metadata_type_detail_view(self):
        self._create_metadata_type()

        response = self.client.get(
            reverse(
                'rest_api:metadatatype-detail',
                args=(self.metadata_type.pk,)
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['label'], TEST_METADATA_TYPE_LABEL
        )

    def test_metadata_type_patch_view(self):
        self._create_metadata_type()

        response = self.client.patch(
            reverse(
                'rest_api:metadatatype-detail',
                args=(self.metadata_type.pk,)
            ), data={
                'label': TEST_METADATA_TYPE_LABEL_2,
                'name': TEST_METADATA_TYPE_NAME_2
            }
        )

        self.assertEqual(response.status_code, 200)

        self.metadata_type.refresh_from_db()

        self.assertEqual(self.metadata_type.label, TEST_METADATA_TYPE_LABEL_2)
        self.assertEqual(self.metadata_type.name, TEST_METADATA_TYPE_NAME_2)

    def test_metadata_type_put_view(self):
        self._create_metadata_type()

        response = self.client.put(
            reverse(
                'rest_api:metadatatype-detail',
                args=(self.metadata_type.pk,)
            ), data={
                'label': TEST_METADATA_TYPE_LABEL_2,
                'name': TEST_METADATA_TYPE_NAME_2
            }
        )

        self.assertEqual(response.status_code, 200)

        self.metadata_type.refresh_from_db()

        self.assertEqual(self.metadata_type.label, TEST_METADATA_TYPE_LABEL_2)
        self.assertEqual(self.metadata_type.name, TEST_METADATA_TYPE_NAME_2)

    def test_metadata_type_list_view(self):
        self._create_metadata_type()

        response = self.client.get(reverse('rest_api:metadatatype-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['results'][0]['label'], TEST_METADATA_TYPE_LABEL
        )


class DocumentTypeMetadataTypeAPITestCase(BaseAPITestCase):
    def setUp(self):
        super(DocumentTypeMetadataTypeAPITestCase, self).setUp()

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

        self.metadata_type = MetadataType.objects.create(
            label=TEST_METADATA_TYPE_LABEL, name=TEST_METADATA_TYPE_NAME
        )

    def tearDown(self):
        self.admin_user.delete()
        self.document_type.delete()
        super(DocumentTypeMetadataTypeAPITestCase, self).tearDown()

    def _create_document_type_metadata_type(self):
        self.document_type_metadata_type = self.document_type.metadata.create(
            metadata_type=self.metadata_type, required=False
        )

    def test_document_type_metadata_type_create_view(self):
        response = self.client.post(
            reverse(
                'rest_api:documenttypemetadatatype-list',
                args=(self.document_type.pk,)
            ), data={
                'metadata_type_pk': self.metadata_type.pk, 'required': False
            }
        )

        self.assertEqual(response.status_code, 201)

        document_type_metadata_type = DocumentTypeMetadataType.objects.first()

        self.assertEqual(response.data['id'], document_type_metadata_type.pk)

    def test_document_type_metadata_type_create_dupicate_view(self):
        self._create_document_type_metadata_type()

        response = self.client.post(
            reverse(
                'rest_api:documenttypemetadatatype-list',
                args=(self.document_type.pk,)
            ), data={
                'metadata_type_pk': self.metadata_type.pk, 'required': False
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.keys()[0], 'non_field_errors')

    def test_document_type_metadata_type_delete_view(self):
        self._create_document_type_metadata_type()

        response = self.client.delete(
            reverse(
                'rest_api:documenttypemetadatatype-detail',
                args=(
                    self.document_type.pk, self.document_type_metadata_type.pk,
                ),
            ),
        )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(self.document_type.metadata.all().count(), 0)

    def test_document_type_metadata_type_list_view(self):
        self._create_document_type_metadata_type()

        response = self.client.get(
            reverse(
                'rest_api:documenttypemetadatatype-list',
                args=(
                    self.document_type.pk,
                ),
            ),
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data['results'][0]['id'],
            self.document_type_metadata_type.pk
        )

    def test_document_type_metadata_type_patch_view(self):
        self._create_document_type_metadata_type()

        response = self.client.patch(
            reverse(
                'rest_api:documenttypemetadatatype-detail',
                args=(
                    self.document_type.pk, self.document_type_metadata_type.pk,
                )
            ), data={
                'required': True
            }
        )

        document_type_metadata_type = DocumentTypeMetadataType.objects.first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(document_type_metadata_type.required, True)

    def test_document_type_metadata_type_put_view(self):
        self._create_document_type_metadata_type()

        response = self.client.put(
            reverse(
                'rest_api:documenttypemetadatatype-detail',
                args=(
                    self.document_type.pk, self.document_type_metadata_type.pk,
                )
            ), data={
                'required': True
            }
        )

        document_type_metadata_type = DocumentTypeMetadataType.objects.first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(document_type_metadata_type.required, True)


class DocumentMetadataAPITestCase(BaseAPITestCase):
    @override_settings(OCR_AUTO_OCR=False)
    def setUp(self):
        super(DocumentMetadataAPITestCase, self).setUp()

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

        self.metadata_type = MetadataType.objects.create(
            label=TEST_METADATA_TYPE_LABEL, name=TEST_METADATA_TYPE_NAME
        )

        self.document_type.metadata.create(
            metadata_type=self.metadata_type, required=False
        )

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object,
            )

    def tearDown(self):
        self.admin_user.delete()
        self.document_type.delete()
        super(DocumentMetadataAPITestCase, self).tearDown()

    def _create_document_metadata(self):
        self.document_metadata = self.document.metadata.create(
            metadata_type=self.metadata_type, value=TEST_METADATA_VALUE
        )

    def test_document_metadata_create_view(self):
        response = self.client.post(
            reverse(
                'rest_api:documentmetadata-list',
                args=(self.document.pk,)
            ), data={
                'metadata_type_pk': self.metadata_type.pk,
                'value': TEST_METADATA_VALUE
            }
        )

        document_metadata = self.document.metadata.first()

        self.assertEqual(response.status_code, 201)

        self.assertEqual(response.data['id'], document_metadata.pk)

        self.assertEqual(document_metadata.metadata_type, self.metadata_type)
        self.assertEqual(document_metadata.value, TEST_METADATA_VALUE)

    def test_document_metadata_create_duplicate_view(self):
        self._create_document_metadata()

        response = self.client.post(
            reverse(
                'rest_api:documentmetadata-list',
                args=(self.document.pk,)
            ), data={
                'metadata_type_pk': self.metadata_type.pk,
                'value': TEST_METADATA_VALUE
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.keys()[0], 'non_field_errors')

    def test_document_metadata_create_invalid_lookup_value_view(self):
        self.metadata_type.lookup = 'invalid,lookup,values,on,purpose'
        self.metadata_type.save()

        response = self.client.post(
            reverse(
                'rest_api:documentmetadata-list',
                args=(self.document.pk,)
            ), data={
                'metadata_type_pk': self.metadata_type.pk,
                'value': TEST_METADATA_VALUE
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.keys()[0], 'non_field_errors')

    def test_document_metadata_delete_view(self):
        self._create_document_metadata()

        response = self.client.delete(
            reverse(
                'rest_api:documentmetadata-detail',
                args=(self.document.pk, self.document_metadata.pk,)
            )
        )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(self.document.metadata.all().count(), 0)

    def test_document_metadata_list_view(self):
        self._create_document_metadata()

        response = self.client.get(
            reverse(
                'rest_api:documentmetadata-list', args=(self.document.pk,)
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data['results'][0]['document']['id'], self.document.pk
        )
        self.assertEqual(
            response.data['results'][0]['metadata_type']['id'],
            self.metadata_type.pk
        )
        self.assertEqual(
            response.data['results'][0]['value'], TEST_METADATA_VALUE
        )
        self.assertEqual(
            response.data['results'][0]['id'], self.document_metadata.pk
        )

    def test_document_metadata_patch_view(self):
        self._create_document_metadata()

        response = self.client.patch(
            reverse(
                'rest_api:documentmetadata-detail',
                args=(self.document.pk, self.document_metadata.pk,)
            ), data={
                'value': TEST_METADATA_VALUE_EDITED
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['value'], TEST_METADATA_VALUE_EDITED
        )

    def test_document_metadata_put_view(self):
        self._create_document_metadata()

        response = self.client.put(
            reverse(
                'rest_api:documentmetadata-detail',
                args=(self.document.pk, self.document_metadata.pk,)
            ), data={
                'value': TEST_METADATA_VALUE_EDITED
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['value'], TEST_METADATA_VALUE_EDITED
        )
