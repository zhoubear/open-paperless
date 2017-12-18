from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

from rest_api.tests import BaseAPITestCase
from user_management.tests.literals import (
    TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME
)

from ..models import Message

from .literals import (
    TEST_LABEL, TEST_LABEL_EDITED, TEST_MESSAGE, TEST_MESSAGE_EDITED
)


@override_settings(OCR_AUTO_OCR=False)
class MOTDAPITestCase(BaseAPITestCase):
    def setUp(self):
        super(MOTDAPITestCase, self).setUp()

        self.admin_user = get_user_model().objects.create_superuser(
            username=TEST_ADMIN_USERNAME, email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )

        self.client.login(
            username=TEST_ADMIN_USERNAME, password=TEST_ADMIN_PASSWORD
        )

    def _create_message(self):
        return Message.objects.create(
            label=TEST_LABEL, message=TEST_MESSAGE
        )

    def test_message_create_view(self):
        response = self.client.post(
            reverse('rest_api:message-list'), {
                'label': TEST_LABEL, 'message': TEST_MESSAGE
            }
        )

        message = Message.objects.first()
        self.assertEqual(response.data['id'], message.pk)
        self.assertEqual(response.data['label'], TEST_LABEL)
        self.assertEqual(response.data['message'], TEST_MESSAGE)

        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.label, TEST_LABEL)
        self.assertEqual(message.message, TEST_MESSAGE)

    def test_message_delete_view(self):
        message = self._create_message()

        self.client.delete(
            reverse('rest_api:message-detail', args=(message.pk,))
        )

        self.assertEqual(Message.objects.count(), 0)

    def test_message_detail_view(self):
        message = self._create_message()

        response = self.client.get(
            reverse('rest_api:message-detail', args=(message.pk,))
        )

        self.assertEqual(
            response.data['label'], TEST_LABEL
        )

    def test_message_patch_view(self):
        message = self._create_message()

        self.client.patch(
            reverse('rest_api:message-detail', args=(message.pk,)),
            {
                'label': TEST_LABEL_EDITED,
                'message': TEST_MESSAGE_EDITED
            }
        )

        message.refresh_from_db()

        self.assertEqual(message.label, TEST_LABEL_EDITED)
        self.assertEqual(message.message, TEST_MESSAGE_EDITED)

    def test_message_put_view(self):
        message = self._create_message()

        self.client.put(
            reverse('rest_api:message-detail', args=(message.pk,)),
            {
                'label': TEST_LABEL_EDITED,
                'message': TEST_MESSAGE_EDITED
            }
        )

        message.refresh_from_db()

        self.assertEqual(message.label, TEST_LABEL_EDITED)
        self.assertEqual(message.message, TEST_MESSAGE_EDITED)
