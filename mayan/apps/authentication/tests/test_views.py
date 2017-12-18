from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from common.tests import BaseTestCase
from smart_settings.classes import Namespace
from user_management.tests.literals import (
    TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD, TEST_USER_PASSWORD_EDITED,
    TEST_ADMIN_USERNAME
)

from ..settings import setting_maximum_session_length

from .literals import TEST_EMAIL_AUTHENTICATION_BACKEND


class UserLoginTestCase(BaseTestCase):
    """
    Test that users can login via the supported authentication methods
    """

    def setUp(self):
        super(UserLoginTestCase, self).setUp()
        Namespace.invalidate_cache_all()

    @override_settings(AUTHENTICATION_LOGIN_METHOD='username')
    def test_normal_behavior(self):
        response = self.client.get(reverse('documents:document_list'))
        self.assertRedirects(
            response,
            'http://testserver/authentication/login/?next=/documents/list/'
        )

    @override_settings(AUTHENTICATION_LOGIN_METHOD='username')
    def test_username_login(self):
        logged_in = self.client.login(
            username=TEST_ADMIN_USERNAME, password=TEST_ADMIN_PASSWORD
        )
        self.assertTrue(logged_in)
        response = self.client.get(reverse('documents:document_list'))
        # We didn't get redirected to the login URL
        self.assertEqual(response.status_code, 200)

    @override_settings(AUTHENTICATION_LOGIN_METHOD='email')
    def test_email_login(self):
        with self.settings(AUTHENTICATION_BACKENDS=(TEST_EMAIL_AUTHENTICATION_BACKEND,)):
            logged_in = self.client.login(
                username=TEST_ADMIN_USERNAME, password=TEST_ADMIN_PASSWORD
            )
            self.assertFalse(logged_in)

            logged_in = self.client.login(
                email=TEST_ADMIN_EMAIL, password=TEST_ADMIN_PASSWORD
            )
            self.assertTrue(logged_in)

            response = self.client.get(reverse('documents:document_list'))
            # We didn't get redirected to the login URL
            self.assertEqual(response.status_code, 200)

    @override_settings(AUTHENTICATION_LOGIN_METHOD='username')
    def test_username_login_via_views(self):
        response = self.client.get(reverse('documents:document_list'))
        self.assertRedirects(
            response,
            'http://testserver/authentication/login/?next=/documents/list/'
        )

        response = self.client.post(
            reverse(settings.LOGIN_URL), {
                'username': TEST_ADMIN_USERNAME,
                'password': TEST_ADMIN_PASSWORD
            }
        )
        response = self.client.get(reverse('documents:document_list'))
        # We didn't get redirected to the login URL
        self.assertEqual(response.status_code, 200)

    @override_settings(AUTHENTICATION_LOGIN_METHOD='email')
    def test_email_login_via_views(self):
        with self.settings(AUTHENTICATION_BACKENDS=(TEST_EMAIL_AUTHENTICATION_BACKEND,)):
            response = self.client.get(reverse('documents:document_list'))
            self.assertRedirects(
                response,
                'http://testserver/authentication/login/?next=/documents/list/'
            )

            response = self.client.post(
                reverse(settings.LOGIN_URL), {
                    'email': TEST_ADMIN_EMAIL, 'password': TEST_ADMIN_PASSWORD
                }, follow=True
            )
            self.assertEqual(response.status_code, 200)

            response = self.client.get(reverse('documents:document_list'))
            # We didn't get redirected to the login URL
            self.assertEqual(response.status_code, 200)

    @override_settings(AUTHENTICATION_LOGIN_METHOD='username')
    def test_username_remember_me(self):
        response = self.client.post(
            reverse(settings.LOGIN_URL), {
                'username': TEST_ADMIN_USERNAME,
                'password': TEST_ADMIN_PASSWORD,
                'remember_me': True
            }, follow=True
        )

        response = self.client.get(reverse('documents:document_list'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            self.client.session.get_expiry_age(),
            setting_maximum_session_length.value
        )
        self.assertFalse(self.client.session.get_expire_at_browser_close())

    @override_settings(AUTHENTICATION_LOGIN_METHOD='username')
    def test_username_dont_remember_me(self):
        response = self.client.post(
            reverse(settings.LOGIN_URL), {
                'username': TEST_ADMIN_USERNAME,
                'password': TEST_ADMIN_PASSWORD,
                'remember_me': False
            }, follow=True
        )

        response = self.client.get(reverse('documents:document_list'))
        self.assertEqual(response.status_code, 200)

        self.assertTrue(self.client.session.get_expire_at_browser_close())

    @override_settings(AUTHENTICATION_LOGIN_METHOD='email')
    def test_email_remember_me(self):
        with self.settings(AUTHENTICATION_BACKENDS=(TEST_EMAIL_AUTHENTICATION_BACKEND,)):
            response = self.client.post(
                reverse(settings.LOGIN_URL), {
                    'email': TEST_ADMIN_EMAIL,
                    'password': TEST_ADMIN_PASSWORD,
                    'remember_me': True
                }, follow=True
            )

            response = self.client.get(reverse('documents:document_list'))
            self.assertEqual(response.status_code, 200)

            self.assertEqual(
                self.client.session.get_expiry_age(),
                setting_maximum_session_length.value
            )
            self.assertFalse(self.client.session.get_expire_at_browser_close())

    @override_settings(AUTHENTICATION_LOGIN_METHOD='email')
    def test_email_dont_remember_me(self):
        with self.settings(AUTHENTICATION_BACKENDS=(TEST_EMAIL_AUTHENTICATION_BACKEND,)):
            response = self.client.post(
                reverse(settings.LOGIN_URL), {
                    'email': TEST_ADMIN_EMAIL,
                    'password': TEST_ADMIN_PASSWORD,
                    'remember_me': False
                }, follow=True
            )

            response = self.client.get(reverse('documents:document_list'))
            self.assertEqual(response.status_code, 200)

            self.assertTrue(self.client.session.get_expire_at_browser_close())

    @override_settings(AUTHENTICATION_LOGIN_METHOD='username')
    def test_password_reset(self):
        response = self.client.post(
            reverse('authentication:password_reset_view'), {
                'email': TEST_ADMIN_EMAIL,
            }, follow=True
        )

        self.assertContains(
            response, text='Password reset email sent!', status_code=200
        )
        self.assertEqual(len(mail.outbox), 1)

        uid_token = mail.outbox[0].body.replace('\n', '').split('/')

        response = self.client.post(
            reverse('authentication:password_reset_confirm_view', args=uid_token[-3:-1]), {
                'new_password1': TEST_USER_PASSWORD_EDITED,
                'new_password2': TEST_USER_PASSWORD_EDITED,
            }, follow=True
        )

        self.assertContains(
            response, text='Password reset complete!', status_code=200
        )

        response = self.client.post(
            reverse(settings.LOGIN_URL), {
                'username': TEST_ADMIN_USERNAME,
                'password': TEST_USER_PASSWORD_EDITED,
                'remember_me': True
            }, follow=True
        )

        response = self.client.get(reverse('documents:document_list'))
        self.assertEqual(response.status_code, 200)
