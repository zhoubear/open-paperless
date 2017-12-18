from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django.utils.encoding import force_text

from documents.models import DocumentType
from documents.tests import TEST_DOCUMENT_TYPE_LABEL, TEST_SMALL_DOCUMENT_PATH
from rest_api.tests import BaseAPITestCase
from user_management.tests.literals import (
    TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME
)

from ..models import Tag

from .literals import (
    TEST_TAG_COLOR, TEST_TAG_COLOR_EDITED, TEST_TAG_LABEL,
    TEST_TAG_LABEL_EDITED
)


@override_settings(OCR_AUTO_OCR=False)
class TagAPITestCase(BaseAPITestCase):
    def setUp(self):
        super(TagAPITestCase, self).setUp()
        self.admin_user = get_user_model().objects.create_superuser(
            username=TEST_ADMIN_USERNAME, email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )

        self.client.login(
            username=TEST_ADMIN_USERNAME, password=TEST_ADMIN_PASSWORD
        )

    def tearDown(self):
        if hasattr(self, 'document_type'):
            self.document_type.delete()
        super(TagAPITestCase, self).tearDown()

    def _create_tag(self):
        return Tag.objects.create(color=TEST_TAG_COLOR, label=TEST_TAG_LABEL)

    def _document_create(self):
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            document = self.document_type.new_document(
                file_object=file_object,
            )

        return document

    def test_tag_create_view(self):
        response = self.client.post(
            reverse('rest_api:tag-list'), {
                'label': TEST_TAG_LABEL, 'color': TEST_TAG_COLOR
            }
        )

        tag = Tag.objects.first()
        self.assertEqual(response.data['id'], tag.pk)
        self.assertEqual(response.data['label'], TEST_TAG_LABEL)
        self.assertEqual(response.data['color'], TEST_TAG_COLOR)

        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(tag.label, TEST_TAG_LABEL)
        self.assertEqual(tag.color, TEST_TAG_COLOR)

    def test_tag_create_with_documents_view(self):
        response = self.client.post(
            reverse('rest_api:tag-list'), {
                'label': TEST_TAG_LABEL, 'color': TEST_TAG_COLOR
            }
        )

        tag = Tag.objects.first()
        self.assertEqual(response.data['id'], tag.pk)
        self.assertEqual(response.data['label'], TEST_TAG_LABEL)
        self.assertEqual(response.data['color'], TEST_TAG_COLOR)

        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(tag.label, TEST_TAG_LABEL)
        self.assertEqual(tag.color, TEST_TAG_COLOR)

    def test_tag_delete_view(self):
        tag = self._create_tag()

        self.client.delete(reverse('rest_api:tag-detail', args=(tag.pk,)))

        self.assertEqual(Tag.objects.count(), 0)

    def test_tag_document_list_view(self):
        tag = self._create_tag()
        document = self._document_create()
        tag.documents.add(document)

        response = self.client.get(
            reverse('rest_api:tag-document-list', args=(tag.pk,))
        )

        self.assertEqual(
            response.data['results'][0]['uuid'], force_text(document.uuid)
        )

    def test_tag_edit_via_patch(self):
        tag = self._create_tag()

        self.client.patch(
            reverse('rest_api:tag-detail', args=(tag.pk,)),
            {
                'label': TEST_TAG_LABEL_EDITED,
                'color': TEST_TAG_COLOR_EDITED
            }
        )

        tag.refresh_from_db()

        self.assertEqual(tag.label, TEST_TAG_LABEL_EDITED)
        self.assertEqual(tag.color, TEST_TAG_COLOR_EDITED)

    def test_tag_edit_via_put(self):
        tag = self._create_tag()

        self.client.put(
            reverse('rest_api:tag-detail', args=(tag.pk,)),
            {
                'label': TEST_TAG_LABEL_EDITED,
                'color': TEST_TAG_COLOR_EDITED
            }
        )

        tag.refresh_from_db()

        self.assertEqual(tag.label, TEST_TAG_LABEL_EDITED)
        self.assertEqual(tag.color, TEST_TAG_COLOR_EDITED)

    def test_document_attach_tag_view(self):
        tag = self._create_tag()
        document = self._document_create()

        self.client.post(
            reverse('rest_api:document-tag-list', args=(document.pk,)),
            {'tag_pk': tag.pk}
        )
        self.assertQuerysetEqual(document.tags.all(), (repr(tag),))

    def test_document_tag_detail_view(self):
        tag = self._create_tag()
        document = self._document_create()
        tag.documents.add(document)

        response = self.client.get(
            reverse('rest_api:document-tag-detail', args=(document.pk, tag.pk))
        )

        self.assertEqual(response.data['label'], tag.label)

    def test_document_tag_list_view(self):
        tag = self._create_tag()
        document = self._document_create()
        tag.documents.add(document)

        response = self.client.get(
            reverse('rest_api:document-tag-list', args=(document.pk,))
        )
        self.assertEqual(response.data['results'][0]['label'], tag.label)

    def test_document_tag_remove_view(self):
        tag = self._create_tag()
        document = self._document_create()
        tag.documents.add(document)

        self.client.delete(
            reverse(
                'rest_api:document-tag-detail', args=(document.pk, tag.pk)
            ),
        )

        self.assertEqual(tag.documents.count(), 0)
