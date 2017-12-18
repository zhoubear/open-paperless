from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)


class LockingBackend(object):
    """
    Base class for the lock backends. Defines the base methods that each
    subclass must define.
    """
    @classmethod
    def acquire_lock(cls, name, timeout=None):
        logger.debug('acquiring lock: %s, timeout: %s', name, timeout)

    @classmethod
    def purge_locks(cls):
        logger.debug('purging locks')

    def release(self):
        logger.debug('releasing lock: %s', self.name)
