from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

from rest_api.tests import BaseAPITestCase
from user_management.tests.literals import (
    TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME
)

from ..models import Key

from .literals import TEST_KEY_DATA, TEST_KEY_FINGERPRINT


@override_settings(OCR_AUTO_OCR=False)
class KeyAPITestCase(BaseAPITestCase):
    def setUp(self):
        super(KeyAPITestCase, self).setUp()
        self.admin_user = get_user_model().objects.create_superuser(
            username=TEST_ADMIN_USERNAME, email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )

        self.client.login(
            username=TEST_ADMIN_USERNAME, password=TEST_ADMIN_PASSWORD
        )

    def _create_key(self):
        return Key.objects.create(key_data=TEST_KEY_DATA)

    def test_key_create_view(self):
        response = self.client.post(
            reverse('rest_api:key-list'), {
                'key_data': TEST_KEY_DATA
            }
        )
        self.assertEqual(response.data['fingerprint'], TEST_KEY_FINGERPRINT)

        key = Key.objects.first()
        self.assertEqual(Key.objects.count(), 1)
        self.assertEqual(key.fingerprint, TEST_KEY_FINGERPRINT)

    def test_key_delete_view(self):
        key = self._create_key()

        self.client.delete(reverse('rest_api:key-detail', args=(key.pk,)))

        self.assertEqual(Key.objects.count(), 0)

    def test_key_detail_view(self):
        key = self._create_key()

        response = self.client.get(
            reverse('rest_api:key-detail', args=(key.pk,))
        )

        self.assertEqual(response.data['fingerprint'], key.fingerprint)
