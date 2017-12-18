from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

from rest_framework.test import APITestCase

from documents.models import DocumentType
from documents.tests.literals import (
    TEST_DOCUMENT_TYPE_LABEL, TEST_SMALL_DOCUMENT_PATH
)
from user_management.tests.literals import (
    TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME
)

from ..models import Comment

from .literals import TEST_COMMENT_TEXT


@override_settings(OCR_AUTO_OCR=False)
class CommentAPITestCase(APITestCase):
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

    def tearDown(self):
        if hasattr(self, 'document_type'):
            self.document_type.delete()

    def _create_comment(self):
        return self.document.comments.create(
            comment=TEST_COMMENT_TEXT, user=self.admin_user
        )

    def test_comment_create_view(self):
        response = self.client.post(
            reverse(
                'rest_api:comment-list', args=(self.document.pk,)
            ), {
                'comment': TEST_COMMENT_TEXT
            }
        )

        self.assertEqual(response.status_code, 201)
        comment = Comment.objects.first()
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(response.data['id'], comment.pk)

    def test_comment_delete_view(self):
        comment = self._create_comment()

        self.client.delete(
            reverse(
                'rest_api:comment-detail', args=(self.document.pk, comment.pk,)
            )
        )

        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_detail_view(self):
        comment = self._create_comment()

        response = self.client.get(
            reverse(
                'rest_api:comment-detail', args=(self.document.pk, comment.pk,)
            )
        )

        self.assertEqual(response.data['comment'], comment.comment)

    def test_comment_list_view(self):
        comment = self._create_comment()

        response = self.client.get(
            reverse('rest_api:comment-list', args=(self.document.pk,))
        )

        self.assertEqual(
            response.data['results'][0]['comment'], comment.comment
        )
