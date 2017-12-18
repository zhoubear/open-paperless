from __future__ import unicode_literals

import datetime
import logging

from django.db import OperationalError, models, transaction
from django.db.utils import IntegrityError
from django.utils.timezone import now

from .exceptions import LockError

logger = logging.getLogger(__name__)


class LockManager(models.Manager):
    def acquire_lock(self, name, timeout=None):
        logger.debug('trying to acquire lock: %s', name)
        lock = self.model(name=name, timeout=timeout)

        try:
            with transaction.atomic():
                lock.save(force_insert=True)
        except IntegrityError as exception:
            logger.debug('IntegrityError: %s', exception)
            # There is already an existing lock
            # Check it's expiration date and if expired, reset it
            try:
                lock = self.model.objects.get(name=name)
            except self.model.DoesNotExist:
                # Table based locking
                logger.debug('lock: %s does not exist', name)
                raise LockError('Unable to acquire lock')

            if now() > lock.creation_datetime + datetime.timedelta(seconds=lock.timeout):
                logger.debug('reseting deleting stale lock: %s', name)
                lock.timeout = timeout
                logger.debug('trying to reacquire stale lock: %s', name)
                lock.save()
                logger.debug('reacquired stale lock: %s', name)
                return lock
            else:
                logger.debug('unable to acquire lock: %s', name)
                raise LockError('Unable to acquire lock')
        except OperationalError as exception:
            raise LockError(
                'Operational error while trying to acquire lock: %s; %s',
                name, exception
            )
        else:
            logger.debug('acquired lock: %s', name)
            return lock
