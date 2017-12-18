from __future__ import unicode_literals

import logging

from django.apps import apps

from .settings import setting_auto_ocr

logger = logging.getLogger(__name__)


def handler_initialize_new_ocr_settings(sender, instance, **kwargs):
    DocumentTypeSettings = apps.get_model(
        app_label='ocr', model_name='DocumentTypeSettings'
    )

    if kwargs['created']:
        DocumentTypeSettings.objects.create(
            document_type=instance, auto_ocr=setting_auto_ocr.value
        )


def handler_ocr_document_version(sender, instance, **kwargs):
    logger.debug('received post_version_upload')
    logger.debug('instance pk: %s', instance.pk)
    if instance.document.document_type.ocr_settings.auto_ocr:
        instance.submit_for_ocr()
