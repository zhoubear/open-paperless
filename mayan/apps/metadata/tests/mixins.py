from __future__ import unicode_literals

from ..models import MetadataType

from .literals import TEST_METADATA_TYPE_NAME, TEST_METADATA_TYPE_LABEL


class MetadataTypeMixin(object):
    def setUp(self):
        super(MetadataTypeMixin, self).setUp()
        self.metadata_type = MetadataType.objects.create(
            name=TEST_METADATA_TYPE_NAME, label=TEST_METADATA_TYPE_LABEL
        )
