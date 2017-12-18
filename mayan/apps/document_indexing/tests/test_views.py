from __future__ import absolute_import, unicode_literals

from documents.tests.test_views import GenericDocumentViewTestCase

from ..models import Index
from ..permissions import (
    permission_document_indexing_create, permission_document_indexing_delete,
    permission_document_indexing_edit, permission_document_indexing_view
)

from .literals import (
    TEST_INDEX_LABEL, TEST_INDEX_LABEL_EDITED, TEST_INDEX_SLUG,
    TEST_INDEX_TEMPLATE_LABEL_EXPRESSION
)


class IndexViewTestCase(GenericDocumentViewTestCase):
    def test_index_create_view_no_permission(self):
        self.login_user()

        response = self.post(
            'indexing:index_setup_create', data={
                'label': TEST_INDEX_LABEL, 'slug': TEST_INDEX_SLUG
            }
        )

        self.assertEquals(response.status_code, 403)
        self.assertEqual(Index.objects.count(), 0)

    def test_index_create_view_with_permission(self):
        self.login_user()

        self.role.permissions.add(
            permission_document_indexing_create.stored_permission
        )

        response = self.post(
            'indexing:index_setup_create', data={
                'label': TEST_INDEX_LABEL, 'slug': TEST_INDEX_SLUG
            }, follow=True
        )

        self.assertContains(response, text='created', status_code=200)
        self.assertEqual(Index.objects.count(), 1)
        self.assertEqual(Index.objects.first().label, TEST_INDEX_LABEL)

    def test_index_delete_view_no_permission(self):
        self.login_user()

        index = Index.objects.create(
            label=TEST_INDEX_LABEL, slug=TEST_INDEX_SLUG
        )

        response = self.post('indexing:index_setup_delete', args=(index.pk,))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Index.objects.count(), 1)

    def test_index_delete_view_with_permission(self):
        self.login_user()

        self.role.permissions.add(
            permission_document_indexing_delete.stored_permission
        )

        index = Index.objects.create(
            label=TEST_INDEX_LABEL, slug=TEST_INDEX_SLUG
        )

        response = self.post(
            'indexing:index_setup_delete', args=(index.pk,), follow=True
        )

        self.assertContains(response, text='deleted', status_code=200)
        self.assertEqual(Index.objects.count(), 0)

    def test_index_edit_view_no_permission(self):
        self.login_user()

        index = Index.objects.create(
            label=TEST_INDEX_LABEL, slug=TEST_INDEX_SLUG
        )

        response = self.post(
            'indexing:index_setup_edit', args=(index.pk,), data={
                'label': TEST_INDEX_LABEL_EDITED, 'slug': TEST_INDEX_SLUG
            }
        )
        self.assertEqual(response.status_code, 403)
        index = Index.objects.get(pk=index.pk)
        self.assertEqual(index.label, TEST_INDEX_LABEL)

    def test_index_edit_view_with_permission(self):
        self.login_user()

        self.role.permissions.add(
            permission_document_indexing_edit.stored_permission
        )

        index = Index.objects.create(
            label=TEST_INDEX_LABEL, slug=TEST_INDEX_SLUG
        )

        response = self.post(
            'indexing:index_setup_edit', args=(index.pk,), data={
                'label': TEST_INDEX_LABEL_EDITED, 'slug': TEST_INDEX_SLUG
            }, follow=True
        )

        index = Index.objects.get(pk=index.pk)
        self.assertContains(response, text='update', status_code=200)
        self.assertEqual(index.label, TEST_INDEX_LABEL_EDITED)

    def create_test_index(self):
        # Create empty index
        index = Index.objects.create(label=TEST_INDEX_LABEL)

        # Add our document type to the new index
        index.document_types.add(self.document_type)

        # Create simple index template
        root = index.template_root
        index.node_templates.create(
            parent=root, expression=TEST_INDEX_TEMPLATE_LABEL_EXPRESSION,
            link_documents=True
        )

        # Rebuild indexes
        Index.objects.rebuild()

        return index

    def test_index_instance_node_view_no_permission(self):
        index = self.create_test_index()

        self.login_user()

        response = self.get(
            'indexing:index_instance_node_view', args=(index.instance_root.pk,)
        )

        self.assertEqual(response.status_code, 403)

    def test_index_instance_node_view_with_permission(self):
        index = self.create_test_index()

        self.login_user()

        self.role.permissions.add(
            permission_document_indexing_view.stored_permission
        )

        response = self.get(
            'indexing:index_instance_node_view', args=(index.instance_root.pk,)
        )

        self.assertContains(response, text=TEST_INDEX_LABEL, status_code=200)
