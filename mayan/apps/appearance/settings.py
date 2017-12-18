from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from smart_settings import Namespace

from .literals import DEFAULT_MAXIMUM_TITLE_LENGTH

namespace = Namespace(name='appearance', label=_('Appearance'))
setting_max_title_length = namespace.add_setting(
    global_name='APPEARANCE_MAXIMUM_TITLE_LENGTH',
    default=DEFAULT_MAXIMUM_TITLE_LENGTH
)
