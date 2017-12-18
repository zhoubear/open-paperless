from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)


def handler_parse_document_version(sender, instance, **kwargs):
    instance.submit_for_parsing()
