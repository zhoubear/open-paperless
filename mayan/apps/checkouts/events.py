from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from events.classes import Event

event_document_auto_check_in = Event(
    name='checkouts_document_auto_check_in',
    label=_('Document automatically checked in')
)
event_document_check_in = Event(
    name='checkouts_document_check_in', label=_('Document checked in')
)
event_document_check_out = Event(
    name='checkouts_document_check_out', label=_('Document checked out')
)
event_document_forceful_check_in = Event(
    name='checkouts_document_forceful_check_in',
    label=_('Document forcefully checked in')
)
