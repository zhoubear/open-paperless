from __future__ import unicode_literals

import logging

from django.apps import apps

from lock_manager import LockError
from lock_manager.runtime import locking_backend
from mayan.celery import app

from .literals import CHECKOUT_EXPIRATION_LOCK_EXPIRE

logger = logging.getLogger(__name__)


@app.task(ignore_result=True)
def task_check_expired_check_outs():
    DocumentCheckout = apps.get_model(
        app_label='checkouts', model_name='DocumentCheckout'
    )

    logger.debug('executing...')
    lock_id = 'task_expired_check_outs'
    try:
        logger.debug('trying to acquire lock: %s', lock_id)
        lock = locking_backend.acquire_lock(
            name=lock_id, timeout=CHECKOUT_EXPIRATION_LOCK_EXPIRE
        )
        logger.debug('acquired lock: %s', lock_id)
        DocumentCheckout.objects.check_in_expired_check_outs()
        lock.release()
    except LockError:
        logger.debug('unable to obtain lock')
