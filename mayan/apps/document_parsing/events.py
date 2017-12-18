from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from events.classes import Event

event_parsing_document_version_submit = Event(
    name='parsing_document_version_submit',
    label=_('Document version submitted for parsing')
)
event_parsing_document_version_finish = Event(
    name='parsing_document_version_finish',
    label=_('Document version parsing finished')
)
