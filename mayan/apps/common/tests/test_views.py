from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.template import Context, Template
from django.test.utils import ContextList
from django.urls import clear_url_caches, reverse

from acls import ModelPermission
from user_management.tests import (
    TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME, TEST_USER_USERNAME,
    TEST_USER_PASSWORD
)

from ..models import ErrorLogEntry
from ..permissions_runtime import permission_error_log_view

from .base import BaseTestCase
from .literals import TEST_VIEW_NAME, TEST_VIEW_URL

TEST_ERROR_LOG_ENTRY_RESULT = 'test_error_log_entry_result_text'


class GenericViewTestCase(BaseTestCase):
    def setUp(self):
        super(GenericViewTestCase, self).setUp()
        self.has_test_view = False

    def tearDown(self):
        from mayan.urls import urlpatterns

        self.client.logout()
        if self.has_test_view:
            urlpatterns.pop(0)
        super(GenericViewTestCase, self).tearDown()

    def add_test_view(self, test_object):
        from mayan.urls import urlpatterns

        def test_view(request):
            template = Template('{{ object }}')
            context = Context(
                {'object': test_object, 'resolved_object': test_object}
            )
            return HttpResponse(template.render(context=context))

        urlpatterns.insert(0, url(TEST_VIEW_URL, test_view, name=TEST_VIEW_NAME))
        clear_url_caches()
        self.has_test_view = True

    def get_test_view(self):
        response = self.get(TEST_VIEW_NAME)
        if isinstance(response.context, ContextList):
            # template widget rendering causes test client response to be
            # ContextList rather than RequestContext. Typecast to dictionary
            # before updating.
            result = dict(response.context).copy()
            result.update({'request': response.wsgi_request})
            return Context(result)
        else:
            response.context.update({'request': response.wsgi_request})
            return Context(response.context)

    def get(self, viewname=None, path=None, *args, **kwargs):
        data = kwargs.pop('data', {})
        follow = kwargs.pop('follow', False)

        if viewname:
            path = reverse(viewname=viewname, *args, **kwargs)

        return self.client.get(
            path=path, data=data, follow=follow
        )

    def login(self, username, password):
        logged_in = self.client.login(username=username, password=password)

        user = get_user_model().objects.get(username=username)

        self.assertTrue(logged_in)
        self.assertTrue(user.is_authenticated)

    def login_user(self):
        self.login(username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD)

    def login_admin_user(self):
        self.login(username=TEST_ADMIN_USERNAME, password=TEST_ADMIN_PASSWORD)

    def logout(self):
        self.client.logout()

    def post(self, viewname=None, path=None, *args, **kwargs):
        data = kwargs.pop('data', {})
        follow = kwargs.pop('follow', False)

        if viewname:
            path = reverse(viewname=viewname, *args, **kwargs)

        return self.client.post(
            path=path, data=data, follow=follow
        )


class CommonViewTestCase(GenericViewTestCase):
    def test_about_view(self):
        self.login_user()

        response = self.get('common:about_view')
        self.assertContains(response, text='About', status_code=200)

    def _create_error_log_entry(self):
        ModelPermission.register(
            model=get_user_model(), permissions=(permission_error_log_view,)
        )
        ErrorLogEntry.objects.register(model=get_user_model())

        self.error_log_entry = self.user.error_logs.create(
            result=TEST_ERROR_LOG_ENTRY_RESULT
        )

    def _request_object_error_log_list(self):
        content_type = ContentType.objects.get_for_model(model=self.user)

        return self.get(
            'common:object_error_list', kwargs={
                'app_label': content_type.app_label,
                'model': content_type.model,
                'object_id': self.user.pk
            }, follow=True
        )

    def test_object_error_list_view_with_permissions(self):
            self._create_error_log_entry()

            self.login_user()
            self.grant_access(
                obj=self.user, permission=permission_error_log_view
            )

            response = self._request_object_error_log_list()

            self.assertContains(
                response=response, text=TEST_ERROR_LOG_ENTRY_RESULT,
                status_code=200
            )

    def test_object_error_list_view_no_permissions(self):
            self._create_error_log_entry()

            self.login_user()

            response = self._request_object_error_log_list()

            self.assertNotContains(
                response=response, text=TEST_ERROR_LOG_ENTRY_RESULT,
                status_code=403
            )
