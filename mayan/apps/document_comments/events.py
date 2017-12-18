from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from events.classes import Event

event_document_comment_create = Event(
    name='document_comment_create',
    label=_('Document comment created')
)
event_document_comment_delete = Event(
    name='document_comment_delete',
    label=_('Document comment deleted')
)
