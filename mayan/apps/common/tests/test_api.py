from __future__ import unicode_literals

from django.urls import reverse

from rest_api.tests import BaseAPITestCase


class CommonAPITestCase(BaseAPITestCase):
    def test_content_type_list_view(self):
        response = self.client.get(reverse('rest_api:content-type-list'))
        self.assertEqual(response.status_code, 200)
