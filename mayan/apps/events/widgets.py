from __future__ import unicode_literals

from django.urls import reverse
from django.utils.safestring import mark_safe

from .classes import Event


def event_object_link(entry, attribute='target'):
    obj = getattr(entry, attribute)

    if obj:
        obj_type = '{}: '.format(obj._meta.verbose_name)
    else:
        obj_type = ''

    return mark_safe(
        '<a href="%(url)s">%(obj_type)s%(label)s</a>' % {
            'url': obj.get_absolute_url() if obj else '#',
            'label': obj or '', 'obj_type': obj_type
        }
    )


def event_type_link(entry):
    return mark_safe(
        '<a href="%(url)s">%(label)s</a>' % {
            'url': reverse('events:events_by_verb', kwargs={'verb': entry.verb}),
            'label': Event.get_label(entry.verb)
        }
    )
