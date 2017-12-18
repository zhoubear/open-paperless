from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from smart_settings import Namespace

DEFAULT_BACKEND = 'lock_manager.backends.file_lock.FileLock'
DEFAULT_LOCK_TIMEOUT_VALUE = 30

namespace = Namespace(name='lock_manager', label=_('Lock manager'))

setting_backend = namespace.add_setting(
    default=DEFAULT_BACKEND,
    global_name='LOCK_MANAGER_DEFAULT_BACKEND',
)

setting_default_lock_timeout = namespace.add_setting(
    default=DEFAULT_LOCK_TIMEOUT_VALUE,
    global_name='LOCK_MANAGER_DEFAULT_LOCK_TIMEOUT',
)
