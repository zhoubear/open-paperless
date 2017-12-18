from __future__ import unicode_literals

import datetime
import logging

from django.utils.timezone import now

from common.literals import TIME_DELTA_UNIT_DAYS
from documents.tests.test_views import GenericDocumentViewTestCase
from sources.links import link_upload_version
from user_management.tests import (
    TEST_USER_PASSWORD, TEST_USER_USERNAME, TEST_ADMIN_PASSWORD,
    TEST_ADMIN_USERNAME,
)

from ..models import DocumentCheckout
from ..permissions import (
    permission_document_checkin, permission_document_checkin_override,
    permission_document_checkout, permission_document_checkout_detail_view
)


class DocumentCheckoutViewTestCase(GenericDocumentViewTestCase):
    def test_checkin_document_view_no_permission(self):
        self.login_user()

        expiration_datetime = now() + datetime.timedelta(days=1)

        DocumentCheckout.objects.checkout_document(
            document=self.document, expiration_datetime=expiration_datetime,
            user=self.user, block_new_version=True
        )

        self.assertTrue(self.document.is_checked_out())

        response = self.post(
            'checkouts:checkin_document', args=(self.document.pk,), follow=True
        )

        self.assertEquals(response.status_code, 403)

        self.assertTrue(self.document.is_checked_out())

    def test_checkin_document_view_with_access(self):
        self.login_user()

        expiration_datetime = now() + datetime.timedelta(days=1)

        DocumentCheckout.objects.checkout_document(
            document=self.document, expiration_datetime=expiration_datetime,
            user=self.user, block_new_version=True
        )

        self.assertTrue(self.document.is_checked_out())

        self.grant_access(
            obj=self.document, permission=permission_document_checkin
        )
        self.grant_access(
            obj=self.document,
            permission=permission_document_checkout_detail_view
        )

        response = self.post(
            'checkouts:checkin_document', args=(self.document.pk,), follow=True
        )

        self.assertEquals(response.status_code, 200)

        self.assertFalse(self.document.is_checked_out())

        self.assertFalse(
            DocumentCheckout.objects.is_document_checked_out(
                document=self.document
            )
        )

    def test_checkout_document_view_no_permission(self):
        self.login_user()

        response = self.post(
            'checkouts:checkout_document', args=(self.document.pk,), data={
                'expiration_datetime_0': 2,
                'expiration_datetime_1': TIME_DELTA_UNIT_DAYS,
                'block_new_version': True
            }, follow=True
        )

        self.assertEquals(response.status_code, 403)

        self.assertFalse(self.document.is_checked_out())

    def test_checkout_document_view_with_access(self):
        self.login_user()
        self.grant_access(
            obj=self.document, permission=permission_document_checkout
        )
        self.grant_access(
            obj=self.document,
            permission=permission_document_checkout_detail_view
        )

        response = self.post(
            'checkouts:checkout_document', args=(self.document.pk,), data={
                'expiration_datetime_0': 2,
                'expiration_datetime_1': TIME_DELTA_UNIT_DAYS,
                'block_new_version': True
            }, follow=True
        )

        self.assertEquals(response.status_code, 200)

        self.assertTrue(self.document.is_checked_out())

    def test_document_new_version_after_checkout(self):
        """
        Gitlab issue #231
        User shown option to upload new version of a document even though it
        is blocked by checkout - v2.0.0b2

        Expected results:
            - Link to upload version view should not resolve
            - Upload version view should reject request
        """
        self.login(
            username=TEST_ADMIN_USERNAME, password=TEST_ADMIN_PASSWORD
        )

        expiration_datetime = now() + datetime.timedelta(days=1)

        DocumentCheckout.objects.checkout_document(
            document=self.document, expiration_datetime=expiration_datetime,
            user=self.admin_user, block_new_version=True
        )

        self.assertTrue(self.document.is_checked_out())

        response = self.post(
            'sources:upload_version', args=(self.document.pk,),
            follow=True
        )

        self.assertContains(
            response, text='blocked from uploading',
            status_code=200
        )

        response = self.get(
            'documents:document_version_list', args=(self.document.pk,),
            follow=True
        )

        # Needed by the url view resolver
        response.context.current_app = None
        resolved_link = link_upload_version.resolve(context=response.context)

        self.assertEqual(resolved_link, None)

    def test_forcefull_check_in_document_view_no_permission(self):
        # Gitlab issue #237
        # Forcefully checking in a document by a user without adequate
        # permissions throws out an error

        # Silence unrelated logging
        logging.getLogger('navigation.classes').setLevel(logging.CRITICAL)

        expiration_datetime = now() + datetime.timedelta(days=1)

        DocumentCheckout.objects.checkout_document(
            document=self.document, expiration_datetime=expiration_datetime,
            user=self.admin_user, block_new_version=True
        )

        self.assertTrue(self.document.is_checked_out())

        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
        )

        self.role.permissions.add(
            permission_document_checkin.stored_permission
        )
        self.role.permissions.add(
            permission_document_checkout.stored_permission
        )

        response = self.post(
            'checkouts:checkin_document', args=(self.document.pk,), follow=True
        )

        self.assertContains(
            response, text='Insufficient permissions', status_code=403
        )

        self.assertTrue(self.document.is_checked_out())

    def test_forcefull_check_in_document_view_with_permission(self):
        expiration_datetime = now() + datetime.timedelta(days=1)

        DocumentCheckout.objects.checkout_document(
            document=self.document, expiration_datetime=expiration_datetime,
            user=self.admin_user, block_new_version=True
        )

        self.assertTrue(self.document.is_checked_out())

        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
        )

        self.role.permissions.add(
            permission_document_checkin.stored_permission
        )
        self.role.permissions.add(
            permission_document_checkin.stored_permission
        )
        self.role.permissions.add(
            permission_document_checkin_override.stored_permission
        )
        self.role.permissions.add(
            permission_document_checkout_detail_view.stored_permission
        )
        response = self.post(
            'checkouts:checkin_document', args=(self.document.pk,), follow=True
        )

        self.assertContains(
            response, text='hecked in successfully', status_code=200
        )

        self.assertFalse(self.document.is_checked_out())
