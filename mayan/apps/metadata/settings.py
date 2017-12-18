from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from smart_settings import Namespace

from .parsers import MetadataParser
from .validators import MetadataValidator

namespace = Namespace(name='metadata', label=_('Metadata'))
setting_available_validators = namespace.add_setting(
    global_name='METADATA_AVAILABLE_VALIDATORS',
    default=MetadataValidator.get_import_paths()
)
setting_available_parsers = namespace.add_setting(
    global_name='METADATA_AVAILABLE_PARSERS',
    default=MetadataParser.get_import_paths()
)
