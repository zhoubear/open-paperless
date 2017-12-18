from __future__ import unicode_literals

import sys
import types

# Useful for very coarse version differentiation.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY34 = sys.version_info[0:2] >= (3, 4)

if PY3:
    dict_type = dict
    dictionary_type = dict
else:
    dict_type = types.DictType
    dictionary_type = types.DictionaryType

try:
    from email.Utils import collapse_rfc2231_value  # NOQA
except ImportError:
    from email.utils import collapse_rfc2231_value  # NOQA
