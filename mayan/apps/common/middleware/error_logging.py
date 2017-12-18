from __future__ import unicode_literals

import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404

logger = logging.getLogger(__name__)


class ErrorLoggingMiddleware(object):
    def process_exception(self, request, exception):
        if not isinstance(exception, (PermissionDenied, Http404)):
            # Don't log non critical exceptions
            logger.exception(
                'Exception caught by request middleware; %s, %s', request,
                exception
            )
