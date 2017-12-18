from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from smart_settings import Namespace

namespace = Namespace(name='signatures', label=_('Document signatures'))
setting_storage_backend = namespace.add_setting(
    global_name='SIGNATURES_STORAGE_BACKEND',
    default='storage.backends.filebasedstorage.FileBasedStorage'
)
