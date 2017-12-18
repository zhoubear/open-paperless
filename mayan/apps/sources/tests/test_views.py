from __future__ import unicode_literals

import os
import shutil

from furl import furl

from django.test import override_settings
from django.urls import reverse

from checkouts.models import NewVersionBlock
from common.tests.test_views import GenericViewTestCase
from common.utils import fs_cleanup, mkdtemp
from documents.models import Document, DocumentType
from documents.permissions import permission_document_create
from documents.tests import (
    TEST_DOCUMENT_DESCRIPTION, TEST_DOCUMENT_TYPE_LABEL,
    TEST_SMALL_DOCUMENT_CHECKSUM, TEST_SMALL_DOCUMENT_PATH
)
from documents.tests.test_views import GenericDocumentViewTestCase
from metadata.tests.literals import TEST_METADATA_VALUE_UNICODE
from metadata.tests.mixins import MetadataTypeMixin

from ..links import link_upload_version
from ..literals import SOURCE_CHOICE_WEB_FORM
from ..models import StagingFolderSource, WebFormSource
from ..permissions import (
    permission_sources_setup_create, permission_sources_setup_delete,
    permission_sources_setup_view, permission_staging_file_delete
)

from .literals import (
    TEST_SOURCE_LABEL, TEST_SOURCE_UNCOMPRESS_N, TEST_STAGING_PREVIEW_WIDTH
)


class DocumentUploadTestCase(GenericDocumentViewTestCase):
    def setUp(self):
        super(DocumentUploadTestCase, self).setUp()
        self.source = WebFormSource.objects.create(
            enabled=True, label=TEST_SOURCE_LABEL,
            uncompress=TEST_SOURCE_UNCOMPRESS_N
        )

        self.document.delete()

    def _request_upload_wizard(self):
        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            return self.post(
                'sources:upload_interactive', args=(self.source.pk,), data={
                    'source-file': file_object,
                    'document_type_id': self.document_type.pk,
                }, follow=True
            )

    def test_upload_wizard_without_permission(self):
        self.login_user()

        response = self._request_upload_wizard()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Document.objects.count(), 0)

    def test_upload_wizard_with_permission(self):
        self.login_user()

        self.grant_permission(permission=permission_document_create)

        response = self._request_upload_wizard()

        self.assertTrue(b'queued' in response.content)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(
            Document.objects.first().checksum, TEST_SMALL_DOCUMENT_CHECKSUM
        )

    def test_upload_wizard_with_document_type_access(self):
        """
        Test uploading of documents by granting the document create
        permssion for the document type to the user
        """

        self.login_user()

        # Create an access control entry giving the role the document
        # create permission for the selected document type.
        self.grant_access(
            obj=self.document_type, permission=permission_document_create
        )

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            response = self.post(
                'sources:upload_interactive', args=(self.source.pk,), data={
                    'source-file': file_object,
                    'document_type_id': self.document_type.pk,
                }, follow=True
            )

        self.assertTrue(b'queued' in response.content)
        self.assertEqual(Document.objects.count(), 1)

    def _request_upload_interactive_view(self):
        return self.get(
            'sources:upload_interactive', data={
                'document_type_id': self.document_type.pk,
            }
        )

    def test_upload_interactive_view_no_permission(self):
        self.login_user()

        response = self._request_upload_interactive_view()

        self.assertEqual(response.status_code, 403)

    def test_upload_interactive_view_with_access(self):
        self.login_user()
        self.grant_access(
            permission=permission_document_create, obj=self.document_type
        )
        response = self._request_upload_interactive_view()

        self.assertContains(
            response, text=self.source.label, status_code=200
        )


class DocumentUploadMetadataTestCase(MetadataTypeMixin, GenericDocumentViewTestCase):
    def setUp(self):
        super(DocumentUploadMetadataTestCase, self).setUp()
        self.source = WebFormSource.objects.create(
            enabled=True, label=TEST_SOURCE_LABEL,
            uncompress=TEST_SOURCE_UNCOMPRESS_N
        )

        self.document.delete()

        self.document_type.metadata.create(
            metadata_type=self.metadata_type, required=True
        )

    def test_unicode_interactive_with_unicode_metadata(self):
        self.login_admin_user()

        url = furl(reverse('sources:upload_interactive'))
        url.args['metadata0_id'] = self.metadata_type.pk
        url.args['metadata0_value'] = TEST_METADATA_VALUE_UNICODE

        # Upload the test document
        with open(TEST_SMALL_DOCUMENT_PATH) as file_descriptor:
            self.post(
                path=url, data={
                    'document-language': 'eng', 'source-file': file_descriptor,
                    'document_type_id': self.document_type.pk,
                }, follow=True
            )
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(
            Document.objects.first().metadata.first().value,
            TEST_METADATA_VALUE_UNICODE
        )


@override_settings(OCR_AUTO_OCR=False)
class DocumentUploadIssueTestCase(GenericViewTestCase):
    def setUp(self):
        super(DocumentUploadIssueTestCase, self).setUp()
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

    def tearDown(self):
        self.document_type.delete()
        super(DocumentUploadIssueTestCase, self).tearDown()

    def test_issue_25(self):
        self.login_admin_user()

        # Create new webform source
        self.post(
            'sources:setup_source_create', args=(SOURCE_CHOICE_WEB_FORM,),
            data={'label': 'test', 'uncompress': 'n', 'enabled': True}
        )
        self.assertEqual(WebFormSource.objects.count(), 1)

        # Upload the test document
        with open(TEST_SMALL_DOCUMENT_PATH) as file_descriptor:
            self.post(
                'sources:upload_interactive', data={
                    'document-language': 'eng', 'source-file': file_descriptor,
                    'document_type_id': self.document_type.pk
                }
            )
        self.assertEqual(Document.objects.count(), 1)

        document = Document.objects.first()
        # Test for issue 25 during creation
        # ** description fields was removed from upload from **
        self.assertEqual(document.description, '')

        # Reset description
        document.description = TEST_DOCUMENT_DESCRIPTION
        document.save()
        self.assertEqual(document.description, TEST_DOCUMENT_DESCRIPTION)

        # Test for issue 25 during editing
        self.post(
            'documents:document_edit', args=(document.pk,), data={
                'description': TEST_DOCUMENT_DESCRIPTION,
                'language': document.language, 'label': document.label
            }
        )
        # Fetch document again and test description
        document = Document.objects.first()
        self.assertEqual(document.description, TEST_DOCUMENT_DESCRIPTION)


class NewDocumentVersionViewTestCase(GenericDocumentViewTestCase):
    def test_new_version_block(self):
        """
        Gitlab issue #231
        User shown option to upload new version of a document even though it
        is blocked by checkout - v2.0.0b2

        Expected results:
            - Link to upload version view should not resolve
            - Upload version view should reject request
        """

        self.login_admin_user()

        NewVersionBlock.objects.block(self.document)

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


class StagingFolderViewTestCase(GenericViewTestCase):
    def setUp(self):
        super(StagingFolderViewTestCase, self).setUp()
        self.temporary_directory = mkdtemp()
        shutil.copy(TEST_SMALL_DOCUMENT_PATH, self.temporary_directory)

        self.filename = os.path.basename(TEST_SMALL_DOCUMENT_PATH)

    def tearDown(self):
        fs_cleanup(self.temporary_directory)
        super(StagingFolderViewTestCase, self).tearDown()

    def test_staging_folder_delete_no_permission(self):
        self.login_user()

        staging_folder = StagingFolderSource.objects.create(
            label=TEST_SOURCE_LABEL,
            folder_path=self.temporary_directory,
            preview_width=TEST_STAGING_PREVIEW_WIDTH,
            uncompress=TEST_SOURCE_UNCOMPRESS_N,
        )

        self.assertEqual(len(list(staging_folder.get_files())), 1)

        staging_file = list(staging_folder.get_files())[0]

        response = self.post(
            'sources:staging_file_delete', args=(
                staging_folder.pk, staging_file.encoded_filename
            ), follow=True
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(list(staging_folder.get_files())), 1)

    def test_staging_folder_delete_with_permission(self):
        self.login_user()

        self.grant_permission(permission=permission_staging_file_delete)

        staging_folder = StagingFolderSource.objects.create(
            label=TEST_SOURCE_LABEL,
            folder_path=self.temporary_directory,
            preview_width=TEST_STAGING_PREVIEW_WIDTH,
            uncompress=TEST_SOURCE_UNCOMPRESS_N,
        )

        self.assertEqual(len(list(staging_folder.get_files())), 1)

        staging_file = list(staging_folder.get_files())[0]

        response = self.post(
            'sources:staging_file_delete', args=(
                staging_folder.pk, staging_file.encoded_filename
            ), follow=True
        )

        self.assertContains(response, 'deleted', status_code=200)
        self.assertEqual(len(list(staging_folder.get_files())), 0)


class SourcesTestCase(GenericDocumentViewTestCase):
    def _create_web_source(self):
        self.source = WebFormSource.objects.create(
            enabled=True, label=TEST_SOURCE_LABEL,
            uncompress=TEST_SOURCE_UNCOMPRESS_N
        )

    def test_source_list_view_with_permission(self):
        self._create_web_source()

        self.login_user()

        self.grant_permission(permission=permission_sources_setup_view)

        response = self.get(viewname='sources:setup_source_list')

        self.assertContains(response, text=self.source.label, status_code=200)

    def test_source_list_view_no_permission(self):
        self._create_web_source()

        self.login_user()

        response = self.get(viewname='sources:setup_source_list')

        self.assertEqual(response.status_code, 403)

    def test_source_create_view_with_permission(self):
        self.login_user()

        self.grant_permission(permission=permission_sources_setup_create)
        self.grant_permission(permission=permission_sources_setup_view)

        response = self.post(
            args=(SOURCE_CHOICE_WEB_FORM,), follow=True,
            viewname='sources:setup_source_create', data={
                'enabled': True, 'label': TEST_SOURCE_LABEL,
                'uncompress': TEST_SOURCE_UNCOMPRESS_N
            }
        )

        webform_source = WebFormSource.objects.first()

        self.assertEqual(webform_source.label, TEST_SOURCE_LABEL)
        self.assertEqual(webform_source.uncompress, TEST_SOURCE_UNCOMPRESS_N)

        self.assertEquals(response.status_code, 200)

    def test_source_create_view_no_permission(self):
        self.login_user()

        self.grant_permission(permission=permission_sources_setup_view)

        response = self.post(
            args=(SOURCE_CHOICE_WEB_FORM,), follow=True,
            viewname='sources:setup_source_create', data={
                'enabled': True, 'label': TEST_SOURCE_LABEL,
                'uncompress': TEST_SOURCE_UNCOMPRESS_N
            }
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(WebFormSource.objects.count(), 0)

    def test_source_delete_view_with_permission(self):
        self._create_web_source()

        self.login_user()

        self.grant_permission(permission=permission_sources_setup_delete)
        self.grant_permission(permission=permission_sources_setup_view)

        response = self.post(
            args=(self.source.pk,), follow=True,
            viewname='sources:setup_source_delete'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(WebFormSource.objects.count(), 0)

    def test_source_delete_view_no_permission(self):
        self._create_web_source()

        self.login_user()

        self.grant_permission(permission=permission_sources_setup_view)

        response = self.post(
            args=(self.source.pk,), follow=True,
            viewname='sources:setup_source_delete'
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(WebFormSource.objects.count(), 1)
