from __future__ import unicode_literals

import logging

from django.apps import apps
from django.db import OperationalError

from lock_manager import LockError
from lock_manager.runtime import locking_backend
from mayan.celery import app

from .literals import DO_OCR_RETRY_DELAY, LOCK_EXPIRE

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=DO_OCR_RETRY_DELAY, ignore_result=True)
def task_do_ocr(self, document_version_pk):
    DocumentVersion = apps.get_model(
        app_label='documents', model_name='DocumentVersion'
    )
    DocumentPageOCRContent = apps.get_model(
        app_label='ocr', model_name='DocumentPageOCRContent'
    )

    lock_id = 'task_do_ocr_doc_version-%d' % document_version_pk
    try:
        logger.debug('trying to acquire lock: %s', lock_id)
        # Acquire lock to avoid doing OCR on the same document version more
        # than once concurrently
        lock = locking_backend.acquire_lock(lock_id, LOCK_EXPIRE)
        logger.debug('acquired lock: %s', lock_id)
        document_version = None
        try:
            document_version = DocumentVersion.objects.get(
                pk=document_version_pk
            )
            logger.info(
                'Starting document OCR for document version: %s',
                document_version
            )
            DocumentPageOCRContent.objects.process_document_version(
                document_version=document_version
            )
        except OperationalError as exception:
            logger.warning(
                'OCR error for document version: %d; %s. Retrying.',
                document_version_pk, exception
            )
            raise self.retry(exc=exception)
        finally:
            lock.release()
    except LockError:
        logger.debug('unable to obtain lock: %s' % lock_id)
