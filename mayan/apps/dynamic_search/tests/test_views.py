from __future__ import unicode_literals

from django.test import override_settings

from common.tests.test_views import GenericViewTestCase
from documents.models import DocumentType
from documents.search import document_search
from documents.tests import TEST_DOCUMENT_TYPE_LABEL, TEST_SMALL_DOCUMENT_PATH


@override_settings(OCR_AUTO_OCR=False)
class Issue46TestCase(GenericViewTestCase):
    """
    Functional tests to make sure issue 46 is fixed
    """

    def setUp(self):
        super(Issue46TestCase, self).setUp()
        self.login_admin_user()

        self.document_count = 4

        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        # Upload many instances of the same test document
        for i in range(self.document_count):
            with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
                self.document_type.new_document(
                    file_object=file_object,
                    label='test document',
                )

    def tearDown(self):
        for document_type in DocumentType.objects.all():
            document_type.delete()
        super(Issue46TestCase, self).tearDown()

    def test_advanced_search_past_first_page(self):
        # Make sure all documents are returned by the search
        model_list, result_set, elapsed_time = document_search.search(
            {'label': 'test document'}, user=self.admin_user
        )
        self.assertEqual(len(result_set), self.document_count)

        with self.settings(COMMON_PAGINATE_BY=2):
            # Funcitonal test for the first page of advanced results
            response = self.get(
                'search:results', args=(document_search.get_full_name(),),
                data={'label': 'test'}
            )

            self.assertContains(
                response, 'Total (1 - 2 out of 4) (Page 1 of 2)',
                status_code=200
            )

            # Functional test for the second page of advanced results
            response = self.get(
                'search:results', args=(document_search.get_full_name(),),
                data={'label': 'test', 'page': 2}
            )
            self.assertContains(
                response, 'Total (3 - 4 out of 4) (Page 2 of 2)',
                status_code=200
            )
