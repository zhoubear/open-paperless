from __future__ import unicode_literals

from django.apps import apps

from .literals import DEFAULT_DOCUMENT_TYPE_LABEL
from .signals import post_initial_document_type
from .tasks import task_scan_duplicates_for


def create_default_document_type(sender, **kwargs):
    DocumentType = apps.get_model(
        app_label='documents', model_name='DocumentType'
    )

    if not DocumentType.objects.count():
        document_type = DocumentType.objects.create(
            label=DEFAULT_DOCUMENT_TYPE_LABEL
        )
        post_initial_document_type.send(
            sender=DocumentType, instance=document_type
        )


def handler_scan_duplicates_for(sender, instance, **kwargs):
    task_scan_duplicates_for.apply_async(
        kwargs={'document_id': instance.document.pk}
    )
