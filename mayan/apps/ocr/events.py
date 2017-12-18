from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from events.classes import Event

event_ocr_document_version_submit = Event(
    name='ocr_document_version_submit',
    label=_('Document version submitted for OCR')
)
event_ocr_document_version_finish = Event(
    name='ocr_document_version_finish',
    label=_('Document version OCR finished')
)
