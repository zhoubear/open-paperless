from __future__ import absolute_import, unicode_literals

import logging

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from common.generics import ConfirmView

from ..permissions import permission_document_tools
from ..tasks import task_clear_image_cache, task_scan_duplicates_all

logger = logging.getLogger(__name__)


class ClearImageCacheView(ConfirmView):
    extra_context = {
        'title': _('Clear the document image cache?')
    }
    view_permission = permission_document_tools

    def view_action(self):
        task_clear_image_cache.apply_async()
        messages.success(
            self.request, _('Document cache clearing queued successfully.')
        )


class ScanDuplicatedDocuments(ConfirmView):
    extra_context = {
        'title': _('Scan for duplicated documents?')
    }
    view_permission = permission_document_tools

    def view_action(self):
        task_scan_duplicates_all.apply_async()
        messages.success(
            self.request, _('Duplicated document scan queued successfully.')
        )
