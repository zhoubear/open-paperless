from __future__ import unicode_literals

import logging

from django.apps import apps

from mayan.celery import app

RETRY_DELAY = 10
logger = logging.getLogger(__name__)


@app.task(bind=True, ignore_result=True)
def task_unverify_key_signatures(self, key_id):
    DetachedSignature = apps.get_model(
        app_label='document_signatures', model_name='DetachedSignature'
    )

    EmbeddedSignature = apps.get_model(
        app_label='document_signatures', model_name='EmbeddedSignature'
    )

    for signature in DetachedSignature.objects.filter(key_id__endswith=key_id).filter(signature_id__isnull=False):
        signature.save()

    for signature in EmbeddedSignature.objects.filter(key_id__endswith=key_id).filter(signature_id__isnull=False):
        signature.save()


@app.task(bind=True, ignore_result=True)
def task_verify_key_signatures(self, key_pk):
    Key = apps.get_model(
        app_label='django_gpg', model_name='Key'
    )

    DetachedSignature = apps.get_model(
        app_label='document_signatures', model_name='DetachedSignature'
    )

    EmbeddedSignature = apps.get_model(
        app_label='document_signatures', model_name='EmbeddedSignature'
    )

    key = Key.objects.get(pk=key_pk)

    for signature in DetachedSignature.objects.filter(key_id__endswith=key.key_id).filter(signature_id__isnull=True):
        signature.save()

    for signature in EmbeddedSignature.objects.filter(key_id__endswith=key.key_id).filter(signature_id__isnull=True):
        signature.save()


@app.task(bind=True, ignore_result=True)
def task_verify_missing_embedded_signature(self):
    EmbeddedSignature = apps.get_model(
        app_label='document_signatures', model_name='EmbeddedSignature'
    )

    for document_version in EmbeddedSignature.objects.unsigned_document_versions():
        task_verify_document_version.apply_async(
            kwargs=dict(document_version_pk=document_version.pk)
        )


@app.task(bind=True, ignore_result=True)
def task_verify_document_version(self, document_version_pk):
    DocumentVersion = apps.get_model(
        app_label='documents', model_name='DocumentVersion'
    )

    EmbeddedSignature = apps.get_model(
        app_label='document_signatures', model_name='EmbeddedSignature'
    )

    document_version = DocumentVersion.objects.get(pk=document_version_pk)
    try:
        EmbeddedSignature.objects.create(document_version=document_version)
    except IOError as exception:
        error_message = 'File missing for document version ID {}; {}'.format(
            document_version_pk, exception
        )
        logger.error(error_message)
        raise IOError(error_message)
