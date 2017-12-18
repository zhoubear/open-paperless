from __future__ import unicode_literals

from django.template import Library
from django.utils.translation import ugettext_lazy as _

register = Library()


@register.filter
def get_choice_value(field):
    try:
        return dict(field.field.choices)[field.value()]
    except TypeError:
        return ', '.join([entry for id, entry in field.field.choices])
    except KeyError:
        return _('None')
