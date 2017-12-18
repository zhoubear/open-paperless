# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import documents.models
import storage.backends.filebasedstorage


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_auto_20150608_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='uuid',
            field=models.CharField(
                default=documents.models.UUID_FUNCTION, max_length=48,
                editable=False
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='documentversion',
            name='file',
            field=models.FileField(
                upload_to=documents.models.UUID_FUNCTION,
                storage=storage.backends.filebasedstorage.FileBasedStorage(),
                verbose_name='File'
            ),
            preserve_default=True,
        ),
    ]
