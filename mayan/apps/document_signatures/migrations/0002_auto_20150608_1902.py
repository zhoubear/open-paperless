# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import storage.backends.filebasedstorage
import document_signatures.models


class Migration(migrations.Migration):

    dependencies = [
        ('document_signatures', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentversionsignature',
            name='has_embedded_signature',
            field=models.BooleanField(
                default=False, verbose_name='Has embedded signature'
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='documentversionsignature',
            name='signature_file',
            field=models.FileField(
                storage=storage.backends.filebasedstorage.FileBasedStorage(),
                upload_to=document_signatures.models.upload_to, null=True,
                verbose_name='Signature file', blank=True
            ),
            preserve_default=True,
        ),
    ]
