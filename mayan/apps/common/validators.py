from __future__ import unicode_literals

import re

from django.core.validators import RegexValidator
from django.utils import six
from django.utils.functional import SimpleLazyObject
from django.utils.translation import ugettext_lazy as _

# These values, if given to validate(), will trigger the self.required check.
EMPTY_VALUES = (None, '', [], (), {})


def _lazy_re_compile(regex, flags=0):
    """Lazily compile a regex with flags."""
    def _compile():
        # Compile the regex if it was not passed pre-compiled.
        if isinstance(regex, six.string_types):
            return re.compile(regex, flags)
        else:
            assert not flags, 'flags must be empty if regex is passed pre-compiled'
            return regex
    return SimpleLazyObject(_compile)


internal_name_re = _lazy_re_compile(r'^[a-zA-Z0-9_]+\Z')
validate_internal_name = RegexValidator(
    internal_name_re, _(
        "Enter a valid 'internal name' consisting of letters, numbers, and "
        "underscores."
    ), 'invalid'
)
