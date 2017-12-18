# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def create_ocr_setting_for_existing_document_types(apps, schema_editor):
    DocumentType = apps.get_model('documents', 'DocumentType')
    DocumentTypeSettings = apps.get_model('ocr', 'DocumentTypeSettings')

    for document_type in DocumentType.objects.all():
        try:
            DocumentTypeSettings.objects.create(document_type=document_type)
        except DocumentTypeSettings.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0016_auto_20150708_0325'),
        ('ocr', '0003_auto_20150617_0401'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentTypeSettings',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'auto_ocr', models.BooleanField(
                        default=True,
                        verbose_name='Automatically queue newly created '
                        'documents for OCR.'
                    )
                ),
                (
                    'document_type', models.OneToOneField(
                        related_name='ocr_settings',
                        verbose_name='Document type',
                        to='documents.DocumentType'
                    )
                ),
            ],
            options={
                'verbose_name': 'Document type settings',
                'verbose_name_plural': 'Document types settings',
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(create_ocr_setting_for_existing_document_types),
    ]
