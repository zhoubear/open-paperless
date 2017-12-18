# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentVersionOCRError',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                (
                    'datetime_submitted', models.DateTimeField(
                        auto_now=True, verbose_name='Date time submitted',
                        db_index=True
                    )
                ),
                (
                    'result', models.TextField(
                        null=True, verbose_name='Result', blank=True
                    )
                ),
                (
                    'document_version', models.ForeignKey(
                        verbose_name='Document version',
                        to='documents.DocumentVersion'
                    )
                ),
            ],
            options={
                'ordering': ('datetime_submitted',),
                'verbose_name': 'Document Version OCR Error',
                'verbose_name_plural': 'Document Version OCR Errors',
            },
            bases=(models.Model,),
        ),
    ]
