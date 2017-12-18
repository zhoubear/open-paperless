from __future__ import absolute_import, unicode_literals

from documents.tests.test_views import GenericDocumentViewTestCase

from ..models import Cabinet
from ..permissions import (
    permission_cabinet_add_document, permission_cabinet_create,
    permission_cabinet_delete, permission_cabinet_edit,
    permission_cabinet_remove_document, permission_cabinet_view
)
from .literals import TEST_CABINET_LABEL, TEST_CABINET_EDITED_LABEL


class CabinetViewTestCase(GenericDocumentViewTestCase):
    def setUp(self):
        super(CabinetViewTestCase, self).setUp()
        self.login_user()

    def _create_cabinet(self):
        self.cabinet = Cabinet.objects.create(label=TEST_CABINET_LABEL)

    def _request_create_cabinet(self, label):
        return self.post(
            'cabinets:cabinet_create', data={
                'label': TEST_CABINET_LABEL
            }
        )

    def test_cabinet_create_view_no_permission(self):
        response = self._request_create_cabinet(label=TEST_CABINET_LABEL)

        self.assertEquals(response.status_code, 403)
        self.assertEqual(Cabinet.objects.count(), 0)

    def test_cabinet_create_view_with_permission(self):
        self.grant_permission(permission=permission_cabinet_create)

        response = self._request_create_cabinet(label=TEST_CABINET_LABEL)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Cabinet.objects.count(), 1)
        self.assertEqual(Cabinet.objects.first().label, TEST_CABINET_LABEL)

    def test_cabinet_create_duplicate_view_with_permission(self):
        self._create_cabinet()
        self.grant_permission(permission=permission_cabinet_create)
        response = self._request_create_cabinet(label=TEST_CABINET_LABEL)

        # HTTP 200 with error message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cabinet.objects.count(), 1)
        self.assertEqual(Cabinet.objects.first().pk, self.cabinet.pk)

    def _request_delete_cabinet(self):
        return self.post('cabinets:cabinet_delete', args=(self.cabinet.pk,))

    def test_cabinet_delete_view_no_permission(self):
        self._create_cabinet()

        response = self._request_delete_cabinet()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Cabinet.objects.count(), 1)

    def test_cabinet_delete_view_with_access(self):
        self._create_cabinet()
        self.grant_access(obj=self.cabinet, permission=permission_cabinet_delete)

        response = self._request_delete_cabinet()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Cabinet.objects.count(), 0)

    def _request_edit_cabinet(self):
        return self.post(
            'cabinets:cabinet_edit', args=(self.cabinet.pk,), data={
                'label': TEST_CABINET_EDITED_LABEL
            }
        )

    def test_cabinet_edit_view_no_permission(self):
        self._create_cabinet()

        response = self._request_edit_cabinet()
        self.assertEqual(response.status_code, 403)
        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.label, TEST_CABINET_LABEL)

    def test_cabinet_edit_view_with_access(self):
        self._create_cabinet()

        self.grant_access(obj=self.cabinet, permission=permission_cabinet_edit)

        response = self._request_edit_cabinet()

        self.assertEqual(response.status_code, 302)
        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.label, TEST_CABINET_EDITED_LABEL)

    def _add_document_to_cabinet(self):
        return self.post(
            'cabinets:cabinet_add_document', args=(self.document.pk,), data={
                'cabinets': self.cabinet.pk
            }
        )

    def test_cabinet_add_document_view_no_permission(self):
        self._create_cabinet()

        self.grant_permission(permission=permission_cabinet_view)

        response = self._add_document_to_cabinet()

        self.assertContains(
            response, text='Select a valid choice.', status_code=200
        )
        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.documents.count(), 0)

    def test_cabinet_add_document_view_with_access(self):
        self._create_cabinet()

        self.grant_access(obj=self.cabinet, permission=permission_cabinet_view)
        self.grant_access(
            obj=self.cabinet, permission=permission_cabinet_add_document
        )
        self.grant_access(
            obj=self.document, permission=permission_cabinet_add_document
        )

        response = self._add_document_to_cabinet()

        self.cabinet.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.cabinet.documents.count(), 1)
        self.assertQuerysetEqual(
            self.cabinet.documents.all(), (repr(self.document),)
        )

    def _request_add_multiple_documents_to_cabinet(self):
        return self.post(
            'cabinets:cabinet_add_multiple_documents', data={
                'id_list': (self.document.pk,), 'cabinets': self.cabinet.pk
            }
        )

    def test_cabinet_add_multiple_documents_view_no_permission(self):
        self._create_cabinet()

        self.grant_permission(permission=permission_cabinet_view)

        response = self._request_add_multiple_documents_to_cabinet()

        self.assertContains(
            response, text='Select a valid choice', status_code=200
        )
        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.documents.count(), 0)

    def test_cabinet_add_multiple_documents_view_with_access(self):
        self._create_cabinet()

        self.grant_access(
            obj=self.cabinet, permission=permission_cabinet_add_document
        )
        self.grant_access(
            obj=self.document, permission=permission_cabinet_add_document
        )

        response = self._request_add_multiple_documents_to_cabinet()

        self.assertEqual(response.status_code, 302)
        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.documents.count(), 1)
        self.assertQuerysetEqual(
            self.cabinet.documents.all(), (repr(self.document),)
        )

    def _request_remove_document_from_cabinet(self):
        return self.post(
            'cabinets:document_cabinet_remove', args=(self.document.pk,),
            data={
                'cabinets': (self.cabinet.pk,),
            }
        )

    def test_cabinet_remove_document_view_no_permission(self):
        self._create_cabinet()

        self.cabinet.documents.add(self.document)

        response = self._request_remove_document_from_cabinet()

        self.assertContains(
            response, text='Select a valid choice', status_code=200
        )

        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.documents.count(), 1)

    def test_cabinet_remove_document_view_with_access(self):
        self._create_cabinet()

        self.cabinet.documents.add(self.document)

        self.grant_access(
            obj=self.cabinet, permission=permission_cabinet_remove_document
        )
        self.grant_access(
            obj=self.document, permission=permission_cabinet_remove_document
        )

        response = self._request_remove_document_from_cabinet()

        self.assertEqual(response.status_code, 302)
        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.documents.count(), 0)

    def _request_cabinet_list(self):
        return self.get('cabinets:cabinet_list')

    def test_cabinet_list_view_no_permission(self):
        self._create_cabinet()
        response = self._request_cabinet_list()
        self.assertNotContains(
            response, text=self.cabinet.label, status_code=200
        )

    def test_cabinet_list_view_with_access(self):
        self._create_cabinet()
        self.grant_access(obj=self.cabinet, permission=permission_cabinet_view)
        response = self._request_cabinet_list()

        self.assertContains(
            response, text=self.cabinet.label, status_code=200
        )
