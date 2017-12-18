from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from smart_settings import Namespace

namespace = Namespace(name='sources', label=_('Sources'))

setting_scanimage_path = namespace.add_setting(
    global_name='SOURCE_SCANIMAGE_PATH', default='/usr/bin/scanimage',
    help_text=_(
        'File path to the scanimage program used to control image scanners.'
    ),
    is_path=True
)
