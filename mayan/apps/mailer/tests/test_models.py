from __future__ import absolute_import, unicode_literals

from django.core import mail

from documents.tests.test_models import GenericDocumentTestCase

from ..models import UserMailer

from .literals import (
    TEST_EMAIL_ADDRESS, TEST_RECIPIENTS_MULTIPLE_COMMA,
    TEST_RECIPIENTS_MULTIPLE_SEMICOLON, TEST_RECIPIENTS_MULTIPLE_MIXED,
    TEST_RECIPIENTS_MULTIPLE_MIXED_LIST, TEST_USER_MAILER_LABEL,
    TEST_USER_MAILER_BACKEND_PATH
)


class ModelTestCase(GenericDocumentTestCase):
    def _create_user_mailer(self):
        self.user_mailer = UserMailer.objects.create(
            default=True,
            enabled=True,
            label=TEST_USER_MAILER_LABEL,
            backend_path=TEST_USER_MAILER_BACKEND_PATH,
            backend_data='{}'
        )

    def test_send_simple(self):
        self._create_user_mailer()
        self.user_mailer.send(to=TEST_EMAIL_ADDRESS)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [TEST_EMAIL_ADDRESS])

    def test_send_attachment(self):
        self._create_user_mailer()
        self.user_mailer.send(
            to=TEST_EMAIL_ADDRESS, document=self.document, as_attachment=True
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [TEST_EMAIL_ADDRESS])
        with self.document.open() as file_object:
            self.assertEqual(
                mail.outbox[0].attachments[0], (
                    self.document.label, file_object.read(),
                    self.document.file_mimetype
                )
            )

    def test_send_multiple_recipients_comma(self):
        self._create_user_mailer()
        self.user_mailer.send(to=TEST_RECIPIENTS_MULTIPLE_COMMA)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].to, TEST_RECIPIENTS_MULTIPLE_COMMA.split(',')
        )

    def test_send_multiple_recipients_semicolon(self):
        self._create_user_mailer()
        self.user_mailer.send(to=TEST_RECIPIENTS_MULTIPLE_SEMICOLON)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].to, TEST_RECIPIENTS_MULTIPLE_SEMICOLON.split(';')
        )

    def test_send_multiple_recipient_mixed(self):
        self._create_user_mailer()
        self.user_mailer.send(to=TEST_RECIPIENTS_MULTIPLE_MIXED)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            list(mail.outbox[0].to), list(TEST_RECIPIENTS_MULTIPLE_MIXED_LIST)
        )
