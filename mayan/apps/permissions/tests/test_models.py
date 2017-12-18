from __future__ import unicode_literals

from django.core.exceptions import PermissionDenied

from common.tests import BaseTestCase

from ..classes import Permission
from ..permissions import permission_role_view


class PermissionTestCase(BaseTestCase):
    def setUp(self):
        super(PermissionTestCase, self).setUp()

    def test_no_permissions(self):
        with self.assertRaises(PermissionDenied):
            Permission.check_permissions(
                requester=self.user, permissions=(permission_role_view,)
            )

    def test_with_permissions(self):
        self.group.user_set.add(self.user)
        self.role.permissions.add(permission_role_view.stored_permission)
        self.role.groups.add(self.group)

        try:
            Permission.check_permissions(
                requester=self.user, permissions=(permission_role_view,)
            )
        except PermissionDenied:
            self.fail('PermissionDenied exception was not expected.')
