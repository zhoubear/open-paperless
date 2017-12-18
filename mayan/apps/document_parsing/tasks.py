from __future__ import unicode_literals

import logging

from django.apps import apps

from mayan.celery import app

logger = logging.getLogger(__name__)


@app.task(ignore_result=True)
def task_parse_document_version(document_version_pk):
    DocumentVersion = apps.get_model(
        app_label='documents', model_name='DocumentVersion'
    )
    DocumentPageContent = apps.get_model(
        app_label='document_parsing', model_name='DocumentPageContent'
    )

    document_version = DocumentVersion.objects.get(
        pk=document_version_pk
    )
    logger.info(
        'Starting parsing for document version: %s', document_version
    )
    DocumentPageContent.objects.process_document_version(
        document_version=document_version
    )
