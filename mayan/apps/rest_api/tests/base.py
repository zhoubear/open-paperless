from __future__ import absolute_import, unicode_literals

from rest_framework.test import APITestCase

from permissions.classes import Permission
from smart_settings.classes import Namespace


class BaseAPITestCase(APITestCase):
    """
    API test case class that invalidates permissions and smart settings
    """

    def setUp(self):
        super(BaseAPITestCase, self).setUp()
        Namespace.invalidate_cache_all()
        Permission.invalidate_cache()
