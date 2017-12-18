from __future__ import unicode_literals

from django.core import mail

from documents.tests.test_views import GenericDocumentViewTestCase

from ..models import UserMailer
from ..permissions import (
    permission_mailing_link, permission_mailing_send_document,
    permission_user_mailer_create, permission_user_mailer_delete,
    permission_user_mailer_use, permission_user_mailer_view
)

from .literals import (
    TEST_EMAIL_ADDRESS, TEST_USER_MAILER_BACKEND_PATH, TEST_USER_MAILER_LABEL
)
from .mailers import TestBackend


class MailerTestMixin(object):
    def _create_user_mailer(self):

        self.user_mailer = UserMailer.objects.create(
            default=True,
            enabled=True,
            label=TEST_USER_MAILER_LABEL,
            backend_path=TEST_USER_MAILER_BACKEND_PATH,
            backend_data='{}'
        )


class MailerViewsTestCase(MailerTestMixin, GenericDocumentViewTestCase):
    def _request_document_link_send(self):
        return self.post(
            'mailer:send_document_link', args=(self.document.pk,),
            data={
                'email': TEST_EMAIL_ADDRESS,
                'user_mailer': self.user_mailer.pk
            },
        )

    def _request_document_send(self):
        return self.post(
            'mailer:send_document', args=(self.document.pk,),
            data={
                'email': TEST_EMAIL_ADDRESS,
                'user_mailer': self.user_mailer.pk
            },
        )

    def _request_user_mailer_create(self):
        return self.post(
            'mailer:user_mailer_create', args=(
                TEST_USER_MAILER_BACKEND_PATH,
            ), data={
                'default': True,
                'enabled': True,
                'label': TEST_USER_MAILER_LABEL,
            }, follow=True
        )

    def _request_user_mailer_delete(self):
        return self.post(
            'mailer:user_mailer_delete', args=(self.user_mailer.pk,)
        )

    def _request_user_mailer_test(self):
        return self.post(
            'mailer:user_mailer_test', args=(self.user_mailer.pk,), data={
                'email': TEST_EMAIL_ADDRESS
            }, follow=True
        )

    def test_mail_link_view_no_permissions(self):
        self._create_user_mailer()
        self.login_user()

        response = self._request_document_link_send()

        self.assertContains(
            response, 'Select a valid choice', status_code=200
        )

    def test_mail_link_view_with_permission(self):
        self._create_user_mailer()
        self.login_user()

        self.grant_permission(permission=permission_mailing_link)
        self.grant_permission(permission=permission_user_mailer_use)

        self._request_document_link_send()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [TEST_EMAIL_ADDRESS])

    def test_mail_document_view_no_permissions(self):
        self._create_user_mailer()
        self.login_user()

        response = self._request_document_send()
        self.assertContains(
            response, 'Select a valid choice', status_code=200
        )

    def test_mail_document_view_with_permission(self):
        self._create_user_mailer()
        self.login_user()

        self.grant_permission(permission=permission_mailing_send_document)
        self.grant_permission(permission=permission_user_mailer_use)

        self._request_document_send()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [TEST_EMAIL_ADDRESS])

    def test_user_mailer_create_view_no_permissions(self):
        self.login_user()
        self.grant_permission(permission=permission_user_mailer_view)

        response = self._request_user_mailer_create()

        self.assertNotContains(
            response, text=TestBackend.label, status_code=403
        )
        self.assertEqual(UserMailer.objects.count(), 0)

    def test_user_mailer_create_view_with_permissions(self):
        self.login_user()
        self.grant_permission(permission=permission_user_mailer_create)
        self.grant_permission(permission=permission_user_mailer_view)

        response = self._request_user_mailer_create()

        self.assertContains(
            response, text=TestBackend.label, status_code=200
        )

        self.assertEqual(UserMailer.objects.count(), 1)

    def test_user_mailer_delete_view_no_permissions(self):
        self._create_user_mailer()
        self.login_user()

        self._request_user_mailer_delete()

        self.assertQuerysetEqual(
            UserMailer.objects.all(), (repr(self.user_mailer),)
        )

    def test_user_mailer_delete_view_with_access(self):
        self._create_user_mailer()
        self.login_user()

        self.grant_access(
            obj=self.user_mailer, permission=permission_user_mailer_delete
        )

        self._request_user_mailer_delete()

        self.assertEqual(UserMailer.objects.count(), 0)

    def test_user_mailer_list_view_no_permissions(self):
        self._create_user_mailer()
        self.login_user()

        response = self.get(
            'mailer:user_mailer_list',
        )
        self.assertNotContains(
            response, text=self.user_mailer.label, status_code=200
        )

    def test_user_mailer_list_view_with_permissions(self):
        self._create_user_mailer()
        self.login_user()

        self.grant_permission(permission=permission_user_mailer_view)

        response = self.get(
            'mailer:user_mailer_list',
        )

        self.assertContains(
            response, text=self.user_mailer.label, status_code=200
        )

    def test_user_mailer_test_view_no_permissions(self):
        self._create_user_mailer()
        self.login_user()

        response = self._request_user_mailer_test()

        self.assertEqual(response.status_code, 403)

        self.assertEqual(len(mail.outbox), 0)

    def test_user_mailer_test_view_with_access(self):
        self._create_user_mailer()
        self.login_user()

        self.grant_access(
            obj=self.user_mailer, permission=permission_user_mailer_use
        )

        response = self._request_user_mailer_test()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [TEST_EMAIL_ADDRESS])
