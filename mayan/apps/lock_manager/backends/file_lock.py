from __future__ import unicode_literals

import logging
import json
import os
import threading
import time
import uuid

from django.core.files import locks
from django.utils.encoding import force_text

from common.settings import setting_temporary_directory

from ..exceptions import LockError
from ..settings import setting_default_lock_timeout

from .base import LockingBackend

lock = threading.Lock()
logger = logging.getLogger(__name__)

lock_file = os.path.join(
    setting_temporary_directory.value, 'mayan_locks.tmp'
)
open(lock_file, 'a').close()
logger.debug('lock_file: %s', lock_file)


class FileLock(LockingBackend):
    lock_file = lock_file

    @classmethod
    def acquire_lock(cls, name, timeout=None):
        super(FileLock, cls).acquire_lock(name=name, timeout=timeout)
        instance = FileLock(
            name=name, timeout=timeout or setting_default_lock_timeout.value
        )
        return instance

    @classmethod
    def purge_locks(cls):
        super(FileLock, cls).purge_locks()
        lock.acquire()
        with open(cls.lock_file, 'r+') as file_object:
            locks.lock(f=file_object, flags=locks.LOCK_EX)
            file_object.seek(0)
            file_object.truncate()
            lock.release()

    def _get_lock_dictionary(self):
        if self.timeout:
            result = {
                'expiration': time.time() + self.timeout,
                'uuid': self.uuid
            }
        else:
            result = {
                'expiration': 0,
                'uuid': self.uuid
            }

        return result

    def __init__(self, name, timeout=None):
        self.name = name
        self.timeout = timeout or setting_default_lock_timeout.value
        self.uuid = force_text(uuid.uuid4())

        lock.acquire()
        with open(self.__class__.lock_file, 'r+') as file_object:
            locks.lock(f=file_object, flags=locks.LOCK_EX)

            data = file_object.read()

            if data:
                file_locks = json.loads(data)
            else:
                file_locks = {}

            if name in file_locks:
                # Someone already got this lock, check to see if it is expired
                if file_locks[name]['expiration'] and time.time() > file_locks[name]['expiration']:
                    # It expires and has expired, we re-acquired it
                    file_locks[name] = self._get_lock_dictionary()
                else:
                    lock.release()
                    raise LockError
            else:
                file_locks[name] = self._get_lock_dictionary()

            file_object.seek(0)
            file_object.truncate()
            file_object.write(json.dumps(file_locks))
            lock.release()

    def release(self):
        super(FileLock, self).release()

        lock.acquire()
        with open(self.__class__.lock_file, 'r+') as file_object:
            locks.lock(f=file_object, flags=locks.LOCK_EX)
            try:
                file_locks = json.loads(file_object.read())
            except EOFError:
                file_locks = {}

            if self.name in file_locks:
                if file_locks[self.name]['uuid'] == self.uuid:
                    file_locks.pop(self.name)
                else:
                    # Lock expired and someone else acquired it
                    pass
            else:
                # Lock expired and someone else released it
                pass

            file_object.seek(0)
            file_object.truncate()
            file_object.write(json.dumps(file_locks))
            lock.release()
