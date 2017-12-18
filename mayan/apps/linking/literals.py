from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

INCLUSION_AND = '&'
INCLUSION_OR = '|'

INCLUSION_CHOICES = (
    (INCLUSION_AND, _('and')),
    (INCLUSION_OR, _('or')),
)

OPERATOR_CHOICES = (
    ('exact', _('is equal to')),
    ('iexact', _('is equal to (case insensitive)')),
    ('contains', _('contains')),
    ('icontains', _('contains (case insensitive)')),
    ('in', _('is in')),
    ('gt', _('is greater than')),
    ('gte', _('is greater than or equal to')),
    ('lt', _('is less than')),
    ('lte', _('is less than or equal to')),
    ('startswith', _('starts with')),
    ('istartswith', _('starts with (case insensitive)')),
    ('endswith', _('ends with')),
    ('iendswith', _('ends with (case insensitive)')),
    ('regex', _('is in regular expression')),
    ('iregex', _('is in regular expression (case insensitive)')),
)
