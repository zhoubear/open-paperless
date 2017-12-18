from __future__ import unicode_literals

import logging
import sys
import traceback

from django.conf import settings
from django.db import models

from .events import event_parsing_document_version_finish
from .parsers import Parser

logger = logging.getLogger(__name__)


class DocumentPageContentManager(models.Manager):
    def process_document_version(self, document_version):
        logger.info(
            'Starting parsing for document version: %s', document_version
        )
        logger.debug('document version: %d', document_version.pk)

        try:
            Parser.parse_document_version(document_version=document_version)
        except Exception as exception:
            logger.error(
                'Parsing error for document version: %d; %s',
                document_version.pk, exception,
            )

            if settings.DEBUG:
                result = []
                type, value, tb = sys.exc_info()
                result.append('%s: %s' % (type.__name__, value))
                result.extend(traceback.format_tb(tb))
                document_version.parsing_errors.create(
                    result='\n'.join(result)
                )
            else:
                document_version.parsing_errors.create(result=exception)
        else:
            logger.info(
                'Parsing complete for document version: %s', document_version
            )
            document_version.parsing_errors.all().delete()

            event_parsing_document_version_finish.commit(
                action_object=document_version.document,
                target=document_version
            )
