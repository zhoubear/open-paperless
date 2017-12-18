# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.utils.encoding import force_text

from common.tests.test_views import GenericViewTestCase
from converter.models import Transformation
from converter.permissions import permission_transformation_delete

from ..literals import (
    DEFAULT_DELETE_PERIOD, DEFAULT_DELETE_TIME_UNIT, PAGE_RANGE_ALL
)
from ..models import DeletedDocument, Document, DocumentType
from ..permissions import (
    permission_document_create, permission_document_delete,
    permission_document_download, permission_document_print,
    permission_document_properties_edit, permission_document_restore,
    permission_document_tools, permission_document_trash,
    permission_document_type_create, permission_document_type_delete,
    permission_document_type_edit, permission_document_type_view,
    permission_document_version_revert, permission_document_version_view,
    permission_document_view, permission_empty_trash
)

from .literals import (
    TEST_DOCUMENT_TYPE_LABEL, TEST_DOCUMENT_TYPE_2_LABEL,
    TEST_DOCUMENT_TYPE_LABEL_EDITED, TEST_DOCUMENT_TYPE_QUICK_LABEL,
    TEST_DOCUMENT_TYPE_QUICK_LABEL_EDITED, TEST_SMALL_DOCUMENT_FILENAME,
    TEST_SMALL_DOCUMENT_PATH, TEST_TRANSFORMATION_ARGUMENT,
    TEST_TRANSFORMATION_NAME, TEST_VERSION_COMMENT
)


@override_settings(OCR_AUTO_OCR=False)
class GenericDocumentViewTestCase(GenericViewTestCase):
    test_document_filename = TEST_SMALL_DOCUMENT_FILENAME

    def setUp(self):
        super(GenericDocumentViewTestCase, self).setUp()
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        self.test_document_path = os.path.join(
            settings.BASE_DIR, 'apps', 'documents', 'tests', 'contrib',
            'sample_documents', self.test_document_filename
        )

        with open(self.test_document_path) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object, label=self.test_document_filename
            )

    def tearDown(self):
        super(GenericDocumentViewTestCase, self).tearDown()
        if self.document_type.pk:
            self.document_type.delete()


class DocumentsViewsTestCase(GenericDocumentViewTestCase):
    def setUp(self):
        super(DocumentsViewsTestCase, self).setUp()
        self.login_user()

    def test_document_view_no_permissions(self):
        response = self.get(
            'documents:document_properties', args=(self.document.pk,)
        )

        self.assertEqual(response.status_code, 403)

    def test_document_view_with_permissions(self):
        self.grant_access(
            obj=self.document, permission=permission_document_view
        )
        response = self.get(
            'documents:document_properties', args=(self.document.pk,),
            follow=True
        )

        self.assertContains(
            response, 'roperties for document', status_code=200
        )

    def test_document_list_view_no_permissions(self):
        response = self.get('documents:document_list')
        self.assertContains(response, 'Total: 0', status_code=200)

    def test_document_list_view_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_document_view
        )
        response = self.get('documents:document_list')
        self.assertContains(response, self.document.label, status_code=200)

    def _request_document_type_edit(self, document_type):
        return self.post(
            'documents:document_document_type_edit',
            args=(self.document.pk,),
            data={'document_type': document_type.pk}
        )

    def test_document_document_type_change_view_no_permissions(self):
        self.assertEqual(
            self.document.document_type, self.document_type
        )

        document_type_2 = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_2_LABEL
        )

        response = self._request_document_type_edit(
            document_type=document_type_2
        )

        self.assertContains(
            response, text='Select a valid choice', status_code=200
        )

        self.assertEqual(
            Document.objects.get(pk=self.document.pk).document_type,
            self.document_type
        )

    def test_document_document_type_change_view_with_permissions(self):
        self.assertEqual(
            self.document.document_type, self.document_type
        )

        document_type_2 = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_2_LABEL
        )

        self.grant_access(
            obj=self.document, permission=permission_document_properties_edit
        )
        self.grant_access(
            obj=document_type_2, permission=permission_document_create
        )

        response = self._request_document_type_edit(
            document_type=document_type_2
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            Document.objects.get(pk=self.document.pk).document_type,
            document_type_2
        )

    def _request_multiple_document_type_edit(self, document_type):
        return self.post(
            'documents:document_multiple_document_type_edit',
            data={
                'id_list': self.document.pk,
                'document_type': document_type.pk
            }
        )

    def test_document_multiple_document_type_change_view_no_permission(self):
        self.assertEqual(
            Document.objects.first().document_type, self.document_type
        )

        document_type_2 = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_2_LABEL
        )

        response = self._request_multiple_document_type_edit(
            document_type=document_type_2
        )

        self.assertContains(
            response, text='Select a valid choice.', status_code=200
        )

        self.assertEqual(
            Document.objects.first().document_type, self.document_type
        )

    def test_document_multiple_document_type_change_view_with_permission(self):
        self.assertEqual(
            Document.objects.first().document_type, self.document_type
        )

        document_type_2 = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_2_LABEL
        )

        self.grant_access(
            obj=self.document, permission=permission_document_properties_edit
        )
        self.grant_access(
            obj=document_type_2, permission=permission_document_create
        )

        response = self._request_multiple_document_type_edit(
            document_type=document_type_2
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            Document.objects.first().document_type, document_type_2
        )

    def _request_document_download_form_view(self):
        return self.get(
            'documents:document_download_form', args=(self.document.pk,),
            follow=True,
        )

    def test_document_download_form_view_no_permission(self):
        response = self._request_document_download_form_view()

        self.assertNotContains(
            response, text=self.document.label, status_code=200
        )

    def test_document_download_form_view_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_document_download
        )
        response = self._request_document_download_form_view()

        self.assertContains(
            response, text=self.document.label, status_code=200
        )

    def test_document_download_view_no_permission(self):
        response = self.get(
            'documents:document_download', args=(self.document.pk,)
        )

        self.assertEqual(response.status_code, 403)

    def test_document_download_view_with_permission(self):
        # Set the expected_content_type for
        # common.tests.mixins.ContentTypeCheckMixin
        self.expected_content_type = '{}; charset=utf-8'.format(
            self.document.file_mimetype
        )

        self.grant_access(
            obj=self.document, permission=permission_document_download
        )
        response = self.get(
            'documents:document_download', args=(self.document.pk,)
        )

        self.assertEqual(response.status_code, 200)

        with self.document.open() as file_object:
            self.assert_download_response(
                response, content=file_object.read(),
                basename=TEST_SMALL_DOCUMENT_FILENAME,
                mime_type=self.document.file_mimetype
            )

    def test_document_multiple_download_view_no_permission(self):
        response = self.get(
            'documents:document_multiple_download',
            data={'id_list': self.document.pk}
        )

        self.assertEqual(response.status_code, 403)

    def test_document_multiple_download_view_with_permission(self):
        # Set the expected_content_type for
        # common.tests.mixins.ContentTypeCheckMixin
        self.expected_content_type = '{}; charset=utf-8'.format(
            self.document.file_mimetype
        )
        self.grant_access(
            obj=self.document, permission=permission_document_download
        )

        response = self.get(
            'documents:document_multiple_download',
            data={'id_list': self.document.pk}
        )

        self.assertEqual(response.status_code, 200)

        with self.document.open() as file_object:
            self.assert_download_response(
                response, content=file_object.read(),
                basename=TEST_SMALL_DOCUMENT_FILENAME,
                mime_type=self.document.file_mimetype
            )

    def _request_document_version_download(self, data=None):
        data = data or {}
        return self.get(
            'documents:document_version_download', args=(
                self.document.latest_version.pk,
            ), data=data
        )

    def test_document_version_download_view_no_permission(self):
        response = self._request_document_version_download()

        self.assertEqual(response.status_code, 403)

    def test_document_version_download_view_with_permission(self):
        # Set the expected_content_type for
        # common.tests.mixins.ContentTypeCheckMixin
        self.expected_content_type = '{}; charset=utf-8'.format(
            self.document.latest_version.mimetype
        )

        self.grant_access(
            obj=self.document, permission=permission_document_download
        )
        response = self._request_document_version_download()

        self.assertEqual(response.status_code, 200)

        with self.document.open() as file_object:
            self.assert_download_response(
                response, content=file_object.read(),
                basename=force_text(self.document.latest_version),
                mime_type='{}; charset=utf-8'.format(
                    self.document.latest_version.mimetype
                )
            )

    def test_document_version_download_preserve_extension_view_with_permission(self):
        # Set the expected_content_type for
        # common.tests.mixins.ContentTypeCheckMixin
        self.expected_content_type = '{}; charset=utf-8'.format(
            self.document.latest_version.mimetype
        )

        self.grant_access(
            obj=self.document, permission=permission_document_download
        )
        response = self._request_document_version_download(
            data={'preserve_extension': True}
        )

        self.assertEqual(response.status_code, 200)

        with self.document.open() as file_object:
            self.assert_download_response(
                response, content=file_object.read(),
                basename=self.document.latest_version.get_rendered_string(
                    preserve_extension=True
                ), mime_type='{}; charset=utf-8'.format(
                    self.document.latest_version.mimetype
                )
            )

    def test_document_update_page_count_view_no_permission(self):
        self.document.pages.all().delete()
        self.assertEqual(self.document.pages.count(), 0)

        response = self.post(
            'documents:document_update_page_count', args=(self.document.pk,)
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.document.pages.count(), 0)

    def test_document_update_page_count_view_with_permission(self):
        # TODO: Revise permission association

        page_count = self.document.pages.count()
        self.document.pages.all().delete()
        self.assertEqual(self.document.pages.count(), 0)

        self.grant_permission(permission=permission_document_tools)

        response = self.post(
            'documents:document_update_page_count',
            args=(self.document.pk,), follow=True
        )
        self.assertContains(response, text='queued', status_code=200)
        self.assertEqual(self.document.pages.count(), page_count)

    def test_document_multiple_update_page_count_view_no_permission(self):
        self.document.pages.all().delete()
        self.assertEqual(self.document.pages.count(), 0)

        response = self.post(
            'documents:document_multiple_update_page_count',
            data={'id_list': self.document.pk}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.document.pages.count(), 0)

    def test_document_multiple_update_page_count_view_with_permission(self):
        page_count = self.document.pages.count()
        self.document.pages.all().delete()
        self.assertEqual(self.document.pages.count(), 0)

        self.grant_permission(permission=permission_document_tools)

        response = self.post(
            'documents:document_multiple_update_page_count',
            data={'id_list': self.document.pk}, follow=True
        )
        self.assertContains(response, text='queued', status_code=200)
        self.assertEqual(self.document.pages.count(), page_count)

    def test_document_clear_transformations_view_no_permission(self):
        document_page = self.document.pages.first()
        content_type = ContentType.objects.get_for_model(document_page)
        transformation = Transformation.objects.create(
            content_type=content_type, object_id=document_page.pk,
            name=TEST_TRANSFORMATION_NAME,
            arguments=TEST_TRANSFORMATION_ARGUMENT
        )

        self.assertQuerysetEqual(
            Transformation.objects.get_for_model(document_page),
            (repr(transformation),)
        )

        self.grant_access(
            obj=self.document, permission=permission_document_view
        )

        response = self.post(
            'documents:document_clear_transformations',
            args=(self.document.pk,)
        )

        self.assertEqual(response.status_code, 302)
        self.assertQuerysetEqual(
            Transformation.objects.get_for_model(document_page),
            (repr(transformation),)
        )

    def test_document_clear_transformations_view_with_access(self):
        document_page = self.document.pages.first()
        content_type = ContentType.objects.get_for_model(document_page)
        transformation = Transformation.objects.create(
            content_type=content_type, object_id=document_page.pk,
            name=TEST_TRANSFORMATION_NAME,
            arguments=TEST_TRANSFORMATION_ARGUMENT
        )
        self.assertQuerysetEqual(
            Transformation.objects.get_for_model(document_page),
            (repr(transformation),)
        )

        self.grant_access(
            obj=self.document, permission=permission_transformation_delete
        )
        self.grant_access(
            obj=self.document, permission=permission_document_view
        )

        response = self.post(
            'documents:document_clear_transformations',
            args=(self.document.pk,)
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Transformation.objects.get_for_model(document_page).count(), 0
        )

    def test_document_multiple_clear_transformations_view_no_permission(self):
        document_page = self.document.pages.first()
        content_type = ContentType.objects.get_for_model(document_page)
        transformation = Transformation.objects.create(
            content_type=content_type, object_id=document_page.pk,
            name=TEST_TRANSFORMATION_NAME,
            arguments=TEST_TRANSFORMATION_ARGUMENT
        )

        self.assertQuerysetEqual(
            Transformation.objects.get_for_model(document_page),
            (repr(transformation),)
        )

        self.grant_permission(permission=permission_document_view)

        response = self.post(
            'documents:document_multiple_clear_transformations',
            data={'id_list': self.document.pk}
        )

        self.assertEqual(response.status_code, 302)
        self.assertQuerysetEqual(
            Transformation.objects.get_for_model(document_page),
            (repr(transformation),)
        )

    def test_document_multiple_clear_transformations_view_with_access(self):
        document_page = self.document.pages.first()
        content_type = ContentType.objects.get_for_model(document_page)
        transformation = Transformation.objects.create(
            content_type=content_type, object_id=document_page.pk,
            name=TEST_TRANSFORMATION_NAME,
            arguments=TEST_TRANSFORMATION_ARGUMENT
        )

        self.assertQuerysetEqual(
            Transformation.objects.get_for_model(document_page),
            (repr(transformation),)
        )

        self.grant_access(
            obj=self.document, permission=permission_document_view
        )
        self.grant_access(
            obj=self.document, permission=permission_transformation_delete
        )

        response = self.post(
            'documents:document_multiple_clear_transformations',
            data={'id_list': self.document.pk}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Transformation.objects.get_for_model(document_page).count(), 0
        )

    def _empty_trash(self):
        return self.post('documents:trash_can_empty')

    def test_trash_can_empty_view_no_permission(self):
        self.document.delete()
        self.assertEqual(DeletedDocument.objects.count(), 1)

        response = self._empty_trash()

        self.assertEqual(response.status_code, 403)

        self.assertEqual(DeletedDocument.objects.count(), 1)

    def test_trash_can_empty_view_with_permission(self):
        self.document.delete()
        self.assertEqual(DeletedDocument.objects.count(), 1)

        self.grant_permission(permission=permission_empty_trash)

        response = self._empty_trash()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(DeletedDocument.objects.count(), 0)
        self.assertEqual(Document.objects.count(), 0)

    def test_document_page_view_no_permissions(self):
        response = self.get(
            'documents:document_page_view', args=(
                self.document.pages.first().pk,
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_document_page_view_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_document_view
        )
        response = self.get(
            'documents:document_page_view', args=(
                self.document.pages.first().pk,
            ),
            follow=True
        )

        self.assertContains(
            response, force_text(self.document.pages.first()), status_code=200
        )

    def _request_print_view(self):
        return self.post(
            'documents:document_print', args=(
                self.document.pk,
            ), data={
                'page_group': PAGE_RANGE_ALL
            }, follow=True
        )

    def test_document_print_view_no_permissions(self):
        response = self._request_print_view()
        self.assertEqual(response.status_code, 403)

    def test_document_print_view_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_document_print
        )
        response = self._request_print_view()
        self.assertEqual(response.status_code, 200)


class DocumentPageViewTestCase(GenericDocumentViewTestCase):
    def setUp(self):
        super(DocumentPageViewTestCase, self).setUp()
        self.login_user()

    def _document_page_list_view(self):
        return self.get(
            'documents:document_pages', args=(self.document.pk,)
        )

    def test_document_page_list_view_no_permission(self):
        response = self._document_page_list_view()
        self.assertEqual(response.status_code, 403)

    def test_document_page_list_view_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_document_view
        )
        response = self._document_page_list_view()
        self.assertContains(
            response, text=self.document.label, status_code=200
        )


class DocumentTypeViewsTestCase(GenericDocumentViewTestCase):
    def setUp(self):
        super(DocumentTypeViewsTestCase, self).setUp()
        self.login_user()

    def _request_document_type_create(self):
        return self.post(
            'documents:document_type_create',
            data={
                'label': TEST_DOCUMENT_TYPE_LABEL,
                'delete_time_period': DEFAULT_DELETE_PERIOD,
                'delete_time_unit': DEFAULT_DELETE_TIME_UNIT
            }, follow=True
        )

    def test_document_type_create_view_no_permission(self):
        self.document_type.delete()

        self.assertEqual(Document.objects.count(), 0)

        # Grant the document type view permission so that the post create
        # redirect works
        self.grant_permission(permission=permission_document_type_view)
        self._request_document_type_create()

        self.assertEqual(DocumentType.objects.count(), 0)

    def test_document_type_create_view_with_permission(self):
        self.document_type.delete()

        self.assertEqual(Document.objects.count(), 0)

        self.grant_permission(permission=permission_document_type_create)
        # Grant the document type view permission so that the post create
        # redirect works
        self.grant_permission(permission=permission_document_type_view)

        response = self._request_document_type_create()

        self.assertContains(response, text='successfully', status_code=200)

        self.assertEqual(DocumentType.objects.count(), 1)
        self.assertEqual(
            DocumentType.objects.first().label, TEST_DOCUMENT_TYPE_LABEL
        )

    def _request_document_type_delete(self):
        return self.post(
            'documents:document_type_delete',
            args=(self.document_type.pk,), follow=True
        )

    def test_document_type_delete_view_no_permission(self):
        # Grant the document type view permission so that the post delete
        # redirect works
        self.grant_permission(permission=permission_document_type_view)

        self._request_document_type_delete()

        self.assertEqual(DocumentType.objects.count(), 1)

    def test_document_type_delete_view_with_access(self):
        self.grant_access(
            obj=self.document_type, permission=permission_document_type_delete
        )
        # Grant the document type view permission so that the post delete
        # redirect works
        self.grant_permission(permission=permission_document_type_view)

        response = self._request_document_type_delete()

        self.assertContains(response, 'successfully', status_code=200)
        self.assertEqual(DocumentType.objects.count(), 0)

    def _request_document_type_edit(self):
        return self.post(
            'documents:document_type_edit',
            args=(self.document_type.pk,),
            data={
                'label': TEST_DOCUMENT_TYPE_LABEL_EDITED,
                'delete_time_period': DEFAULT_DELETE_PERIOD,
                'delete_time_unit': DEFAULT_DELETE_TIME_UNIT
            }, follow=True
        )

    def test_document_type_edit_view_no_permission(self):
        self._request_document_type_edit()

        self.assertEqual(
            DocumentType.objects.get(pk=self.document_type.pk).label,
            TEST_DOCUMENT_TYPE_LABEL
        )

    def test_document_type_edit_view_with_access(self):
        self.grant_access(
            obj=self.document_type, permission=permission_document_type_edit
        )

        # Grant the document type view permission so that the post delete
        # redirect works
        self.grant_permission(permission=permission_document_type_view)

        response = self._request_document_type_edit()

        self.assertContains(response, 'successfully', status_code=200)

        self.assertEqual(
            DocumentType.objects.get(pk=self.document_type.pk).label,
            TEST_DOCUMENT_TYPE_LABEL_EDITED
        )

    def _request_quick_label_create(self):
        return self.post(
            'documents:document_type_filename_create',
            args=(self.document_type.pk,),
            data={
                'filename': TEST_DOCUMENT_TYPE_QUICK_LABEL,
            }, follow=True
        )

    def test_document_type_quick_label_create_no_permission(self):
        self.grant_access(
            obj=self.document_type, permission=permission_document_type_view
        )
        self._request_quick_label_create()

        self.assertEqual(self.document_type.filenames.count(), 0)

    def test_document_type_quick_label_create_with_access(self):
        self.grant_access(
            obj=self.document_type, permission=permission_document_type_view
        )
        self.grant_access(
            obj=self.document_type, permission=permission_document_type_edit
        )

        response = self._request_quick_label_create()

        self.assertContains(response, 'reated', status_code=200)
        self.assertEqual(self.document_type.filenames.count(), 1)

    def _create_quick_label(self):
        self.document_type_filename = self.document_type.filenames.create(
            filename=TEST_DOCUMENT_TYPE_QUICK_LABEL
        )

    def _request_quick_label_edit(self):
        return self.post(
            'documents:document_type_filename_edit',
            args=(self.document_type_filename.pk,),
            data={
                'filename': TEST_DOCUMENT_TYPE_QUICK_LABEL_EDITED,
            }, follow=True
        )

    def test_document_type_quick_label_edit_no_permission(self):
        self._create_quick_label()
        self.grant_access(
            obj=self.document_type, permission=permission_document_type_view
        )
        response = self._request_quick_label_edit()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            self.document_type_filename.filename,
            TEST_DOCUMENT_TYPE_QUICK_LABEL
        )

    def test_document_type_quick_label_edit_with_access(self):
        self.grant_access(
            obj=self.document_type, permission=permission_document_type_edit
        )
        self.grant_access(
            obj=self.document_type, permission=permission_document_type_view
        )

        self._create_quick_label()
        response = self._request_quick_label_edit()
        self.assertEqual(response.status_code, 200)

        self.document_type_filename.refresh_from_db()
        self.assertEqual(
            self.document_type_filename.filename,
            TEST_DOCUMENT_TYPE_QUICK_LABEL_EDITED
        )

    def _request_quick_label_delete(self):
        return self.post(
            'documents:document_type_filename_delete',
            args=(self.document_type_filename.pk,),
            follow=True
        )

    def test_document_type_quick_label_delete_no_permission(self):
        self._create_quick_label()
        self.grant_access(
            obj=self.document_type, permission=permission_document_type_view
        )
        self._request_quick_label_delete()

        self.assertEqual(
            self.document_type.filenames.count(), 1
        )
        self.assertEqual(
            self.document_type.filenames.first().filename,
            TEST_DOCUMENT_TYPE_QUICK_LABEL
        )

    def test_document_type_quick_label_delete_with_access(self):
        self.grant_access(
            obj=self.document_type, permission=permission_document_type_edit
        )
        self.grant_access(
            obj=self.document_type, permission=permission_document_type_view
        )

        self._create_quick_label()
        response = self._request_quick_label_delete()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.document_type.filenames.count(), 0
        )


class DocumentVersionTestCase(GenericDocumentViewTestCase):
    def setUp(self):
        super(DocumentVersionTestCase, self).setUp()
        self.login_user()

    def test_document_version_list_no_permission(self):
        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document.new_version(
                comment=TEST_VERSION_COMMENT, file_object=file_object
            )

        response = self.get(
            'documents:document_version_list', args=(self.document.pk,)
        )

        self.assertEqual(response.status_code, 403)

    def test_document_version_list_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_document_version_view
        )

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document.new_version(
                comment=TEST_VERSION_COMMENT, file_object=file_object
            )

        response = self.get(
            'documents:document_version_list', args=(self.document.pk,)
        )

        self.assertContains(response, TEST_VERSION_COMMENT, status_code=200)

    def test_document_version_revert_no_permission(self):
        first_version = self.document.latest_version

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document.new_version(
                file_object=file_object
            )

        response = self.post(
            'documents:document_version_revert', args=(first_version.pk,)
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.document.versions.count(), 2)

    def test_document_version_revert_with_access(self):
        first_version = self.document.latest_version

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document.new_version(
                file_object=file_object
            )

        self.grant_access(
            obj=self.document, permission=permission_document_version_revert
        )

        response = self.post(
            'documents:document_version_revert', args=(first_version.pk,),
            follow=True
        )

        self.assertContains(response, 'reverted', status_code=200)
        self.assertEqual(self.document.versions.count(), 1)


class DeletedDocumentTestCase(GenericDocumentViewTestCase):
    def setUp(self):
        super(DeletedDocumentTestCase, self).setUp()
        self.login_user()

    def test_document_restore_view_no_permission(self):
        self.document.delete()
        self.assertEqual(Document.objects.count(), 0)

        response = self.post(
            'documents:document_restore', args=(self.document.pk,)
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(DeletedDocument.objects.count(), 1)
        self.assertEqual(Document.objects.count(), 0)

    def test_document_restore_view_with_access(self):
        self.document.delete()
        self.assertEqual(Document.objects.count(), 0)

        self.grant_access(
            obj=self.document, permission=permission_document_restore
        )
        response = self.post(
            'documents:document_restore', args=(self.document.pk,),
            follow=True
        )
        self.assertContains(response, text='restored', status_code=200)
        self.assertEqual(DeletedDocument.objects.count(), 0)
        self.assertEqual(Document.objects.count(), 1)

    def test_document_trash_no_permissions(self):
        response = self.post(
            'documents:document_trash', args=(self.document.pk,)
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(DeletedDocument.objects.count(), 0)
        self.assertEqual(Document.objects.count(), 1)

    def test_document_trash_with_access(self):
        self.grant_access(
            obj=self.document, permission=permission_document_trash
        )

        response = self.post(
            'documents:document_trash', args=(self.document.pk,),
            follow=True
        )

        self.assertContains(response, text='success', status_code=200)
        self.assertEqual(DeletedDocument.objects.count(), 1)
        self.assertEqual(Document.objects.count(), 0)

    def test_document_delete_no_permissions(self):
        self.document.delete()
        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(DeletedDocument.objects.count(), 1)

        response = self.post(
            'documents:document_delete', args=(self.document.pk,),
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(DeletedDocument.objects.count(), 1)

    def test_document_delete_with_access(self):
        self.document.delete()
        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(DeletedDocument.objects.count(), 1)

        self.grant_access(
            obj=self.document, permission=permission_document_delete
        )

        response = self.post(
            'documents:document_delete', args=(self.document.pk,),
            follow=True
        )

        self.assertContains(response, text='success', status_code=200)
        self.assertEqual(DeletedDocument.objects.count(), 0)
        self.assertEqual(Document.objects.count(), 0)

    def test_deleted_document_list_view_no_permissions(self):
        self.document.delete()

        response = self.get('documents:document_list_deleted')

        self.assertNotContains(response, self.document.label, status_code=200)

    def test_deleted_document_list_view_with_access(self):
        self.document.delete()

        self.grant_access(
            obj=self.document, permission=permission_document_view
        )
        response = self.get('documents:document_list_deleted')

        self.assertContains(response, self.document.label, status_code=200)


class DuplicatedDocumentsViewsTestCase(GenericDocumentViewTestCase):
    def setUp(self):
        super(DuplicatedDocumentsViewsTestCase, self).setUp()
        self.login_user()

    def _upload_duplicate_document(self):
        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document_duplicate = self.document_type.new_document(
                file_object=file_object, label=TEST_SMALL_DOCUMENT_FILENAME
            )

    def _request_duplicated_document_list(self):
        return self.get('documents:duplicated_document_list')

    def _request_document_duplicates_list(self):
        return self.get(
            'documents:document_duplicates_list', args=(self.document.pk,)
        )

    def test_duplicated_document_list_no_permissions(self):
        self._upload_duplicate_document()
        response = self._request_duplicated_document_list()

        self.assertNotContains(
            response, text=self.document.label, status_code=200
        )

    def test_duplicated_document_list_with_access(self):
        self._upload_duplicate_document()
        self.grant_access(
            obj=self.document, permission=permission_document_view
        )
        self.grant_access(
            obj=self.document_duplicate,
            permission=permission_document_view
        )
        response = self._request_duplicated_document_list()

        self.assertContains(
            response, text=self.document.label, status_code=200
        )

    def test_document_duplicates_list_no_permissions(self):
        self._upload_duplicate_document()
        response = self._request_document_duplicates_list()

        self.assertEqual(response.status_code, 403)

    def test_document_duplicates_list_with_access(self):
        self._upload_duplicate_document()
        self.grant_access(
            obj=self.document, permission=permission_document_view
        )
        self.grant_access(
            obj=self.document_duplicate,
            permission=permission_document_view
        )
        response = self._request_document_duplicates_list()

        self.assertContains(
            response, text=self.document.label, status_code=200
        )
