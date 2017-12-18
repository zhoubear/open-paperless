from __future__ import unicode_literals

import logging

from django.apps import apps

from mayan.celery import app

logger = logging.getLogger(__name__)


@app.task(ignore_result=True)
def task_remove_metadata_type(document_type_id, metadata_type_id):
    DocumentMetadata = apps.get_model(
        app_label='metadata', model_name='DocumentMetadata'
    )

    DocumentMetadata.objects.filter(
        document__document_type__id=document_type_id,
        metadata_type__id=metadata_type_id
    ).delete()


@app.task(ignore_result=True)
def task_add_required_metadata_type(document_type_id, metadata_type_id):
    DocumentType = apps.get_model(
        app_label='documents', model_name='DocumentType'
    )

    MetadataType = apps.get_model(
        app_label='metadata', model_name='MetadataType'
    )

    metadata_type = MetadataType.objects.get(pk=metadata_type_id)

    for document in DocumentType.objects.get(pk=document_type_id).documents.all():
        document.metadata.create(metadata_type=metadata_type)
