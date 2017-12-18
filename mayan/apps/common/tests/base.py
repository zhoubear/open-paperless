from __future__ import absolute_import, unicode_literals

from django.test import TestCase

from django_downloadview import assert_download_response

from permissions.classes import Permission
from smart_settings.classes import Namespace

from .mixins import (
    ContentTypeCheckMixin, OpenFileCheckMixin, TempfileCheckMixin, UserMixin
)


class BaseTestCase(UserMixin, ContentTypeCheckMixin, OpenFileCheckMixin, TempfileCheckMixin, TestCase):
    """
    This is the most basic test case class any test in the project should use.
    """
    assert_download_response = assert_download_response

    def setUp(self):
        super(BaseTestCase, self).setUp()
        Namespace.invalidate_cache_all()
        Permission.invalidate_cache()
