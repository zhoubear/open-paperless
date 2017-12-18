from __future__ import unicode_literals

import glob
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

if getattr(settings, 'COMMON_TEST_FILE_HANDLES', False):
    import psutil

from acls.models import AccessControlList
from permissions.models import Role
from permissions.tests.literals import TEST_ROLE_LABEL
from user_management.tests import (
    TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME, TEST_ADMIN_EMAIL,
    TEST_GROUP_NAME, TEST_USER_EMAIL, TEST_USER_USERNAME, TEST_USER_PASSWORD
)

from ..settings import setting_temporary_directory


class ContentTypeCheckMixin(object):
    expected_content_type = 'text/html; charset=utf-8'

    def _pre_setup(self):
        super(ContentTypeCheckMixin, self)._pre_setup()
        test_instance = self

        class CustomClient(self.client_class):
            def request(self, *args, **kwargs):
                response = super(CustomClient, self).request(*args, **kwargs)

                content_type = response._headers['content-type'][1]
                test_instance.assertEqual(
                    content_type, test_instance.expected_content_type,
                    msg='Unexpected response content type: {}, expected: {}.'.format(
                        content_type, test_instance.expected_content_type
                    )
                )

                return response

        self.client = CustomClient()


class OpenFileCheckMixin(object):
    def _get_descriptor_count(self):
        process = psutil.Process()
        return process.num_fds()

    def _get_open_files(self):
        process = psutil.Process()
        return process.open_files()

    def setUp(self):
        super(OpenFileCheckMixin, self).setUp()
        if getattr(settings, 'COMMON_TEST_FILE_HANDLES', False):
            self._open_files = self._get_open_files()

    def tearDown(self):
        if getattr(settings, 'COMMON_TEST_FILE_HANDLES', False) and not getattr(self, '_skip_file_descriptor_test', False):
            for new_open_file in self._get_open_files():
                self.assertFalse(
                    new_open_file not in self._open_files,
                    msg='File descriptor leak. The number of file descriptors '
                    'at the start and at the end of the test are not the same.'
                )

            self._skip_file_descriptor_test = False

        super(OpenFileCheckMixin, self).tearDown()


class TempfileCheckMixin(object):
    # Ignore the jvmstat instrumentation and GitLab's CI .config files
    # Ignore LibreOffice fontconfig cache dir
    ignore_globs = ('hsperfdata_*', '.config', '.cache')

    def _get_temporary_entries(self):
        ignored_result = []

        # Expand globs by joining the temporary directory and then flattening
        # the list of lists into a single list
        for item in self.ignore_globs:
            ignored_result.extend(
                glob.glob(
                    os.path.join(setting_temporary_directory.value, item)
                )
            )

        # Remove the path and leave only the expanded filename
        ignored_result = map(lambda x: os.path.split(x)[-1], ignored_result)

        return set(
            os.listdir(setting_temporary_directory.value)
        ) - set(ignored_result)

    def setUp(self):
        super(TempfileCheckMixin, self).setUp()
        if getattr(settings, 'COMMON_TEST_TEMP_FILES', False):
            self._temporary_items = self._get_temporary_entries()

    def tearDown(self):
        if getattr(settings, 'COMMON_TEST_TEMP_FILES', False):
            final_temporary_items = self._get_temporary_entries()
            self.assertEqual(
                self._temporary_items, final_temporary_items,
                msg='Orphan temporary file. The number of temporary files and/or '
                'directories at the start and at the end of the test are not the '
                'same. Orphan entries: {}'.format(
                    ','.join(final_temporary_items - self._temporary_items)
                )
            )
        super(TempfileCheckMixin, self).tearDown()


class UserMixin(object):
    def setUp(self):
        super(UserMixin, self).setUp()
        self.admin_user = get_user_model().objects.create_superuser(
            username=TEST_ADMIN_USERNAME, email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )

        self.user = get_user_model().objects.create_user(
            username=TEST_USER_USERNAME, email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )

        self.group = Group.objects.create(name=TEST_GROUP_NAME)
        self.role = Role.objects.create(label=TEST_ROLE_LABEL)
        self.group.user_set.add(self.user)
        self.role.groups.add(self.group)

    def grant_access(self, permission, obj):
        AccessControlList.objects.grant(
            permission=permission, role=self.role, obj=obj
        )

    def grant_permission(self, permission):
        self.role.permissions.add(
            permission.stored_permission
        )
