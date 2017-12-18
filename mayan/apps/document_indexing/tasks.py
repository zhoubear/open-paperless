from __future__ import unicode_literals

import logging

from django.apps import apps
from django.db import OperationalError

from mayan.celery import app
from lock_manager import LockError

from .literals import RETRY_DELAY

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=RETRY_DELAY, max_retries=None, ignore_result=True)
def task_delete_empty(self):
    IndexInstanceNode = apps.get_model(
        app_label='document_indexing', model_name='IndexInstanceNode'
    )

    try:
        IndexInstanceNode.objects.delete_empty()
    except LockError as exception:
        raise self.retry(exc=exception)


@app.task(bind=True, default_retry_delay=RETRY_DELAY, max_retries=None, ignore_result=True)
def task_remove_document(self, document_id):
    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )
    IndexInstanceNode = apps.get_model(
        app_label='document_indexing', model_name='IndexInstanceNode'
    )

    try:
        document = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        # Document was deleted before we could execute, abort
        pass
    else:
        try:
            IndexInstanceNode.objects.remove_document(document=document)
        except LockError as exception:
            raise self.retry(exc=exception)


@app.task(bind=True, default_retry_delay=RETRY_DELAY, max_retries=None, ignore_result=True)
def task_index_document(self, document_id):
    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )
    Index = apps.get_model(
        app_label='document_indexing', model_name='Index'
    )

    try:
        document = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        # Document was deleted before we could execute, abort about
        # updating
        pass
    else:
        try:
            Index.objects.index_document(document=document)
        except OperationalError as exception:
            logger.warning(
                'Operational error while trying to index document: '
                '%s; %s', document, exception
            )
            raise self.retry(exc=exception)
        except LockError as exception:
            logger.warning(
                'Unable to acquire lock for document %s; %s ',
                document, exception
            )
            raise self.retry(exc=exception)


@app.task(bind=True, default_retry_delay=RETRY_DELAY, ignore_result=True)
def task_rebuild_index(self, index_id):
    Index = apps.get_model(
        app_label='document_indexing', model_name='Index'
    )

    try:
        index = Index.objects.get(pk=index_id)
        index.rebuild()
    except LockError as exception:
        # This index is being rebuilt by another task, retry later
        raise self.retry(exc=exception)
