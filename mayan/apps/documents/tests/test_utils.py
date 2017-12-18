from __future__ import unicode_literals

from common.tests import BaseTestCase

from ..utils import parse_range


class DocumentUtilsTestCase(BaseTestCase):
    def test_parse_range(self):
        self.assertEqual(
            parse_range('1'), [1]
        )

        self.assertEqual(
            parse_range('1-5'), [1, 2, 3, 4, 5]
        )

        self.assertEqual(
            parse_range('2,4,6'), [2, 4, 6]
        )

        self.assertEqual(
            parse_range('2,4,6-8'), [2, 4, 6, 7, 8]
        )
