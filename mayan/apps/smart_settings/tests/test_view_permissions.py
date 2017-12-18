from __future__ import absolute_import, unicode_literals

from common.tests.test_views import GenericViewTestCase

from ..permissions import permission_settings_view


class SmartSettingViewPermissionsTestCase(GenericViewTestCase):
    def setUp(self):
        super(SmartSettingViewPermissionsTestCase, self).setUp()
        self.login_user()

    def test_view_access_denied(self):
        response = self.get('settings:namespace_list')

        self.assertEqual(response.status_code, 403)

        response = self.get(
            'settings:namespace_detail', args=('common',)
        )
        self.assertEqual(response.status_code, 403)

    def test_view_access_permitted(self):
        self.grant_permission(permission=permission_settings_view)

        response = self.get('settings:namespace_list')
        self.assertEqual(response.status_code, 200)

        response = self.get(
            'settings:namespace_detail', args=('common',)
        )
        self.assertEqual(response.status_code, 200)
