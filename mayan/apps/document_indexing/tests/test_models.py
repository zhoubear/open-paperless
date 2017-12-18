from __future__ import unicode_literals

from django.test import override_settings
from django.utils.encoding import force_text

from common.tests import BaseTestCase
from documents.models import DocumentType
from documents.tests import TEST_SMALL_DOCUMENT_PATH, TEST_DOCUMENT_TYPE_LABEL
from metadata.models import MetadataType, DocumentTypeMetadataType

from ..models import Index, IndexInstanceNode, IndexTemplateNode

from .literals import (
    TEST_INDEX_LABEL, TEST_INDEX_TEMPLATE_METADATA_EXPRESSION,
    TEST_METADATA_TYPE_LABEL, TEST_METADATA_TYPE_NAME
)


@override_settings(OCR_AUTO_OCR=False)
class IndexTestCase(BaseTestCase):
    def setUp(self):
        super(IndexTestCase, self).setUp()
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object
            )

    def tearDown(self):
        self.document_type.delete()
        super(IndexTestCase, self).tearDown()

    def test_indexing(self):
        metadata_type = MetadataType.objects.create(
            name=TEST_METADATA_TYPE_NAME, label=TEST_METADATA_TYPE_LABEL
        )
        DocumentTypeMetadataType.objects.create(
            document_type=self.document_type, metadata_type=metadata_type
        )

        # Create empty index
        index = Index.objects.create(label=TEST_INDEX_LABEL)

        # Add our document type to the new index
        index.document_types.add(self.document_type)

        # Create simple index template
        root = index.template_root
        index.node_templates.create(
            parent=root, expression=TEST_INDEX_TEMPLATE_METADATA_EXPRESSION,
            link_documents=True
        )

        # Add document metadata value to trigger index node instance creation
        self.document.metadata.create(
            metadata_type=metadata_type, value='0001'
        )
        self.assertEqual(
            list(
                IndexInstanceNode.objects.values_list('value', flat=True)
            ), ['', '0001']
        )

        # Check that document is in instance node
        instance_node = IndexInstanceNode.objects.get(value='0001')
        self.assertQuerysetEqual(
            instance_node.documents.all(), [repr(self.document)]
        )

        # Change document metadata value to trigger index node instance update
        document_metadata = self.document.metadata.get(
            metadata_type=metadata_type
        )
        document_metadata.value = '0002'
        document_metadata.save()
        self.assertEqual(
            list(
                IndexInstanceNode.objects.values_list('value', flat=True)
            ), ['', '0002']
        )

        # Check that document is in new instance node
        instance_node = IndexInstanceNode.objects.get(value='0002')
        self.assertQuerysetEqual(
            instance_node.documents.all(), [repr(self.document)]
        )

        # Check node instance is destoyed when no metadata is available
        self.document.metadata.get(metadata_type=metadata_type).delete()
        self.assertEqual(
            list(
                IndexInstanceNode.objects.values_list('value', flat=True)
            ), ['']
        )

        # Add document metadata value again to trigger index node instance
        # creation
        self.document.metadata.create(
            metadata_type=metadata_type, value='0003'
        )
        self.assertEqual(
            list(
                IndexInstanceNode.objects.values_list('value', flat=True)
            ), ['', '0003']
        )

        # Check node instance is destroyed when no documents are contained
        self.document.delete()

        # Document is in trash, index structure should remain unchanged
        self.assertEqual(
            list(
                IndexInstanceNode.objects.values_list('value', flat=True)
            ), ['', '0003']
        )

        # Document deleted, index structure should update
        self.document.delete()
        self.assertEqual(
            list(
                IndexInstanceNode.objects.values_list('value', flat=True)
            ), ['']
        )

    def test_rebuild_all_indexes(self):
        # Add metadata type and connect to document type
        metadata_type = MetadataType.objects.create(name='test', label='test')
        DocumentTypeMetadataType.objects.create(
            document_type=self.document_type, metadata_type=metadata_type
        )

        # Add document metadata value
        self.document.metadata.create(
            metadata_type=metadata_type, value='0001'
        )

        # Create empty index
        index = Index.objects.create(label='test')
        self.assertEqual(list(Index.objects.all()), [index])

        # Add our document type to the new index
        index.document_types.add(self.document_type)
        self.assertQuerysetEqual(
            index.document_types.all(), [repr(self.document_type)]
        )

        # Create simple index template
        root = index.template_root
        index.node_templates.create(
            parent=root, expression='{{ document.metadata_value_of.test }}',
            link_documents=True
        )
        self.assertEqual(
            list(
                IndexTemplateNode.objects.values_list('expression', flat=True)
            ), ['', '{{ document.metadata_value_of.test }}']
        )

        # There should be no index instances
        self.assertEqual(list(IndexInstanceNode.objects.all()), [])

        # Rebuild all indexes
        Index.objects.rebuild()

        # Check that document is in instance node
        instance_node = IndexInstanceNode.objects.get(value='0001')
        self.assertQuerysetEqual(
            instance_node.documents.all(), [repr(self.document)]
        )

    def test_dual_level_dual_document_index(self):
        """
        Test creation of an index instance with two first levels with different
        values and two second levels with the same value but as separate
        children of each of the first levels. GitLab issue #391
        """
        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document_2 = self.document_type.new_document(
                file_object=file_object
            )

        # Create empty index
        index = Index.objects.create(label=TEST_INDEX_LABEL)

        # Add our document type to the new index
        index.document_types.add(self.document_type)

        # Create simple index template
        root = index.template_root
        level_1 = index.node_templates.create(
            parent=root, expression='{{ document.uuid }}',
            link_documents=False
        )

        index.node_templates.create(
            parent=level_1, expression='{{ document.label }}',
            link_documents=True
        )

        Index.objects.rebuild()

        self.assertEqual(
            [instance.value for instance in IndexInstanceNode.objects.all().order_by('pk')],
            [
                '', force_text(self.document_2.uuid), self.document_2.label,
                force_text(self.document.uuid), self.document.label
            ]
        )

    def test_multi_level_template_with_no_result_parent(self):
        """
        On a two level template if the first level doesn't return a result
        the indexing should stop. GitLab issue #391.
        """
        index = Index.objects.create(label=TEST_INDEX_LABEL)
        index.document_types.add(self.document_type)

        level_1 = index.node_templates.create(
            parent=index.template_root,
            expression='',
            link_documents=True
        )

        index.node_templates.create(
            parent=level_1, expression='{{ document.label }}',
            link_documents=True
        )

        Index.objects.rebuild()
