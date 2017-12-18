from __future__ import unicode_literals

from common.tests.test_views import GenericViewTestCase

from ..classes import CeleryQueue
from ..permissions import permission_task_view

from .literals import TEST_QUEUE_LABEL, TEST_QUEUE_NAME


class TaskManagerViewTestCase(GenericViewTestCase):
    def setUp(self):
        super(TaskManagerViewTestCase, self).setUp()
        self.test_queue = CeleryQueue(
            label=TEST_QUEUE_LABEL, name=TEST_QUEUE_NAME
        )

    def _request_active_task_list(self):
        return self.get(
            viewname='task_manager:queue_active_task_list',
            args=(self.test_queue.name,), follow=True
        )

    def _request_queue_list(self):
        return self.get(
            viewname='task_manager:queue_list', follow=True
        )

    def _request_reserved_task_list(self):
        return self.get(
            viewname='task_manager:queue_reserved_task_list',
            args=(self.test_queue.name,), follow=True
        )

    def _request_scheduled_task_list(self):
        return self.get(
            viewname='task_manager:queue_scheduled_task_list',
            args=(self.test_queue.name,), follow=True
        )

    def test_queue_list_view_no_permissions(self):
        self.login_user()

        response = self._request_queue_list()

        self.assertEqual(response.status_code, 403)

    def test_queue_list_view_with_permissions(self):
        self.login_user()

        self.grant_permission(permission=permission_task_view)

        response = self._request_queue_list()

        self.assertContains(
            response, text=self.test_queue.name, status_code=200
        )

    def test_active_task_list_view_no_permissions(self):
        self.login_user()

        response = self._request_active_task_list()

        self.assertEqual(response.status_code, 403)

    def test_active_task_list_view_with_permissions(self):
        self.login_user()

        self.grant_permission(permission=permission_task_view)

        response = self._request_active_task_list()

        self.assertEqual(response.status_code, 200)

    def test_reserved_task_list_view_no_permissions(self):
        self.login_user()

        response = self._request_reserved_task_list()

        self.assertEqual(response.status_code, 403)

    def test_reserved_task_list_view_with_permissions(self):
        self.login_user()

        self.grant_permission(permission=permission_task_view)

        response = self._request_reserved_task_list()

        self.assertEqual(response.status_code, 200)

    def test_scheduled_task_list_view_no_permissions(self):
        self.login_user()

        response = self._request_scheduled_task_list()

        self.assertEqual(response.status_code, 403)

    def test_scheduled_task_list_view_with_permissions(self):
        self.login_user()

        self.grant_permission(permission=permission_task_view)

        response = self._request_scheduled_task_list()

        self.assertEqual(response.status_code, 200)
